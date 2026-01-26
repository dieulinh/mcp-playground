#!/usr/bin/env python3
"""
Simple HTTP API wrapper for the AI Shape Generator MCP server.
Allows frontend applications to call the AI shape generation tools via REST API.

Run with: python api_server.py
Server runs on http://localhost:5000
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import logging
from dotenv import load_dotenv
from server import (
    generate_shapes, list_shapes, modify_shape, delete_shape,
    arrange_shapes, generate_palette, apply_style_to_shapes,
    batch_modify_shapes, generate_pattern, analyze_canvas, generate_icon,
    generate_data_visualization
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# API Routes

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "AI Shape Generator API",
        "version": "1.0.0"
    })


def transform_shape_for_canvas(shape):
    """
    Transform AI-generated shape format to canvas-compatible format.
    Triangles need special handling to convert x,y,width,height to points array.
    """
    if shape.get('type') == 'triangle' and 'points' not in shape:
        # Convert triangle from x,y,width,height to points array
        x = shape.get('x', 0)
        y = shape.get('y', 0)
        width = shape.get('width', 100)
        height = shape.get('height', 100)
        
        # Create points for triangle (top center, bottom left, bottom right)
        shape['points'] = [
            {'x': x + width / 2, 'y': y},  # Top center
            {'x': x, 'y': y + height},      # Bottom left
            {'x': x + width, 'y': y + height}  # Bottom right
        ]
        # Remove x, y, width, height as they're not needed with points
        shape.pop('x', None)
        shape.pop('y', None)
        shape.pop('width', None)
        shape.pop('height', None)
    
    return shape


@app.route('/generate-shapes', methods=['POST'])
@app.route('/api/ai/generate-shapes', methods=['POST'])
def api_generate_shapes():
    """Generate shapes from natural language request."""
    try:
        data = request.get_json()
        
        if not data or 'request' not in data:
            return jsonify({"error": "Missing 'request' parameter"}), 400
        
        ai_request = data['request']
        canvas_width = data.get('canvasWidth', 1200)
        canvas_height = data.get('canvasHeight', 600)
        params = data.get('params', {}) or {}
        viz_type = params.get('type') or params.get('viz_type')

        # If no explicit params, try to infer simple chart data from the request text
        if not viz_type and isinstance(ai_request, str):
            rq = ai_request.lower()
            if 'bar chart' in rq or 'barchart' in rq or 'bar-chart' in rq:
                viz_type = 'bar_chart'
            elif 'pie chart' in rq or 'piechart' in rq or 'pie-chart' in rq:
                viz_type = 'pie_chart'
            elif 'table' in rq or 'data table' in rq or 'datatable' in rq:
                viz_type = 'table'

        # If we detected a viz type, attempt to parse labels and values from the request
        if viz_type and not params.get('data'):
            import re
            # Pattern: "of A,B,C with values 10,20,15" (case-insensitive)
            m = re.search(r"of\s+([A-Za-z0-9,\s]+?)\s+(?:with|and)\s+values?\s+([0-9,\s]+)", ai_request, re.IGNORECASE)
            if m:
                raw_labels = m.group(1)
                raw_values = m.group(2)
                labels = [s.strip() for s in re.split(r",|;", raw_labels) if s.strip()]
                values = []
                for v in re.split(r",|;", raw_values):
                    try:
                        values.append(float(v.strip()))
                    except Exception:
                        pass
                if labels and values and len(labels) == len(values):
                    params['data'] = {'labels': labels, 'values': values}
                    params['type'] = viz_type
                    logger.info(f"Parsed viz data from request: type={viz_type}, labels={labels}, values={values}")
                else:
                    logger.info("Could not parse structured viz data from request")
        
        logger.info(f"Generating shapes for: {ai_request} (viz_type={viz_type})")

        # If we have params.type and params.data, route to the visualization generator
        if params.get('type') and params.get('data') and params.get('type') in ('table', 'bar_chart', 'pie_chart'):
            result = generate_data_visualization(params['data'], params['type'], canvas_width, canvas_height)
        else:
            result = generate_shapes(ai_request, canvas_width, canvas_height)
        
        if "error" in result:
            return jsonify(result), 400
        
        # Transform shapes to canvas-compatible format
        if 'shapes' in result:
            result['shapes'] = [transform_shape_for_canvas(shape) for shape in result['shapes']]
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error in generate_shapes endpoint: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/ai/list-shapes', methods=['POST'])
def api_list_shapes():
    """List all shapes on canvas."""
    try:
        data = request.get_json() or {}
        shapes = data.get('shapes', [])
        
        result = list_shapes(shapes)
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error in list_shapes endpoint: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/ai/modify-shape', methods=['POST'])
def api_modify_shape():
    """Modify a specific shape."""
    try:
        data = request.get_json()
        
        if not data or 'shapes' not in data or 'shape_index' not in data:
            return jsonify({"error": "Missing required parameters"}), 400
        
        shapes = data['shapes']
        shape_index = data['shape_index']
        modifications = data.get('modifications', {})
        
        result = modify_shape(shapes, shape_index, modifications)
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error in modify_shape endpoint: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/ai/modify-group', methods=['POST'])
def api_modify_group():
    """Modify shapes in a group either via explicit modifications or by an AI request.

    Payload options:
    - { shapes: [...], group: { id, name, objectIndices }, modifications: { ... } }
      Applies `modifications` to each shape at indices in `group.objectIndices`.

    - { request: "make group red and outlined", canvasWidth, canvasHeight, group: { ... } }
      Calls the AI generator to produce replacement shapes for the group's intent and returns them
      so the frontend can replace or merge as it sees fit.
    """
    try:
        data = request.get_json() or {}

        group = data.get('group')
        if not group:
            return jsonify({"error": "Missing 'group' parameter"}), 400

        shapes = data.get('shapes', [])
        modifications = data.get('modifications')
        ai_request = data.get('request')
        canvas_width = data.get('canvasWidth', 1200)
        canvas_height = data.get('canvasHeight', 600)

        # If explicit modifications provided, apply to each index in group.objectIndices
        if modifications is not None:
            if not isinstance(shapes, list):
                return jsonify({"error": "'shapes' must be an array when using modifications"}), 400

            indices = group.get('objectIndices', []) or []
            modified_shapes = json.loads(json.dumps(shapes))
            modified_count = 0
            for idx in indices:
                if isinstance(idx, int) and 0 <= idx < len(modified_shapes):
                    for k, v in modifications.items():
                        modified_shapes[idx][k] = v
                    modified_count += 1

            logger.info(f"Applied modifications to {modified_count} shapes in group {group.get('id')}")
            return jsonify({
                "success": True,
                "message": f"Modified {modified_count} shapes in group",
                "shapes": modified_shapes,
                "group": group
            }), 200

        # Otherwise, if an AI request is provided, generate shapes for the group's request
        if ai_request:
            logger.info(f"AI modify request for group {group.get('id')}: {ai_request}")

            # If caller provided the group's shapes, ask the AI to modify those shapes
            if isinstance(shapes, list) and len(shapes) > 0:
                logger.info(f"modify-group received {len(shapes)} source shapes for group {group.get('id')}")
                # Build a prompt that includes the original shapes and the instruction
                try:
                    shapes_json = json.dumps(shapes)
                except Exception:
                    shapes_json = str(shapes)

                composite_request = (
                    f"You are given an array of canvas shape objects in JSON.\n"
                    f"Original shapes: {shapes_json}\n"
                    f"Instruction: {ai_request}\n"
                    "Modify the original shapes according to the instruction and return a JSON object with a single key 'shapes' containing the modified shapes array."
                )

                result = generate_shapes(composite_request, canvas_width, canvas_height)
                if 'error' in result:
                    logger.error(f"AI generate error for modify-group: {result}")
                    return jsonify(result), 400

                generated = result.get('shapes', [])
                logger.info(f"AI returned {len(generated)} generated shapes for modify-group (group {group.get('id')})")
                # Transform shapes for canvas compatibility
                generated = [transform_shape_for_canvas(s) for s in generated]

                # Fallback: if AI returned no shapes, return the original shapes back so frontend can duplicate
                if not generated:
                    logger.warning(f"AI returned no shapes for modify-group; falling back to original shapes (group {group.get('id')})")
                    # Ensure original shapes are transformed too
                    try:
                        original_transformed = [transform_shape_for_canvas(s) for s in shapes]
                    except Exception:
                        original_transformed = shapes
                    generated = original_transformed

                return jsonify({
                    "success": True,
                    "message": "Generated modified shapes for group",
                    "generated": generated,
                    "group": group
                }), 200
            else:
                # Fallback behavior: generate new shapes from the instruction alone
                logger.info(f"Generating AI replacement shapes for group {group.get('id')}: {ai_request}")
                result = generate_shapes(ai_request, canvas_width, canvas_height)
                if 'error' in result:
                    logger.error(f"AI generate error for modify-group fallback: {result}")
                    return jsonify(result), 400

                # Transform shapes to canvas-compatible format
                if 'shapes' in result:
                    result['shapes'] = [transform_shape_for_canvas(shape) for shape in result['shapes']]

                generated = result.get('shapes', [])
                logger.info(f"AI returned {len(generated)} generated shapes for modify-group (fallback, group {group.get('id')})")

                if not generated:
                    logger.warning(f"AI fallback returned no shapes; returning empty array for group {group.get('id')}")

                return jsonify({
                    "success": True,
                    "message": "Generated replacement shapes for group",
                    "generated": generated,
                    "group": group
                }), 200

        return jsonify({"error": "Either 'modifications' or 'request' must be provided"}), 400

    except Exception as e:
        logger.error(f"Error in modify_group endpoint: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/ai/delete-shape', methods=['POST'])
def api_delete_shape():
    """Delete a shape from canvas."""
    try:
        data = request.get_json()
        
        if not data or 'shapes' not in data or 'shape_index' not in data:
            return jsonify({"error": "Missing required parameters"}), 400
        
        shapes = data['shapes']
        shape_index = data['shape_index']
        
        result = delete_shape(shapes, shape_index)
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error in delete_shape endpoint: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/ai/arrange-shapes', methods=['POST'])
def api_arrange_shapes():
    """Arrange shapes in a pattern."""
    try:
        data = request.get_json()
        
        if not data or 'shapes' not in data or 'arrangement_type' not in data:
            return jsonify({"error": "Missing required parameters"}), 400
        
        shapes = data['shapes']
        arrangement_type = data['arrangement_type']
        spacing = data.get('spacing', 20)
        # Support both camelCase and snake_case for canvas dimensions
        canvas_width = data.get('canvas_width') or data.get('canvasWidth', 1200)
        canvas_height = data.get('canvas_height') or data.get('canvasHeight', 600)
        
        logger.info(f"Arranging {len(shapes)} shapes in {arrangement_type} pattern with canvas {canvas_width}x{canvas_height}")
        
        result = arrange_shapes(shapes, arrangement_type, spacing, canvas_width, canvas_height)
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error in arrange_shapes endpoint: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/ai/generate-palette', methods=['POST'])
def api_generate_palette():
    """Generate a color palette."""
    try:
        data = request.get_json() or {}
        color_scheme = data.get('color_scheme', 'vibrant')
        
        result = generate_palette(color_scheme)
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error in generate_palette endpoint: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/ai/apply-style', methods=['POST'])
def api_apply_style():
    """Apply visual style to shapes."""
    try:
        data = request.get_json()
        
        if not data or 'shapes' not in data or 'style' not in data:
            return jsonify({"error": "Missing required parameters"}), 400
        
        shapes = data['shapes']
        style = data['style']
        
        result = apply_style_to_shapes(shapes, style)
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error in apply_style endpoint: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/ai/batch-modify', methods=['POST'])
def api_batch_modify():
    """Modify multiple shapes at once."""
    try:
        data = request.get_json()
        
        if not data or 'shapes' not in data:
            return jsonify({"error": "Missing required parameters"}), 400
        
        shapes = data['shapes']
        filter_type = data.get('filter_type', 'all')
        modifications = data.get('modifications', {})
        
        result = batch_modify_shapes(shapes, filter_type, modifications)
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error in batch_modify endpoint: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/ai/generate-pattern', methods=['POST'])
def api_generate_pattern():
    """Generate a pattern of shapes."""
    try:
        data = request.get_json()
        
        if not data or 'pattern_type' not in data:
            return jsonify({"error": "Missing 'pattern_type' parameter"}), 400
        
        pattern_type = data['pattern_type']
        count = data.get('count', 10)
        canvas_width = data.get('canvas_width', 1200)
        canvas_height = data.get('canvas_height', 600)
        
        result = generate_pattern(pattern_type, count, canvas_width, canvas_height)
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error in generate_pattern endpoint: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/ai/analyze-canvas', methods=['POST'])
def api_analyze_canvas():
    """Analyze canvas content."""
    try:
        data = request.get_json() or {}
        shapes = data.get('shapes', [])
        
        result = analyze_canvas(shapes)
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error in analyze_canvas endpoint: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/ai/generate-data-visualization', methods=['POST'])
def api_generate_data_visualization():
    """Generate data visualizations like tables, charts, graphs."""
    try:
        data_param = request.get_json()
        
        if not data_param or 'data' not in data_param:
            return jsonify({"error": "Missing 'data' parameter"}), 400
        
        data = data_param['data']
        viz_type = data_param.get('viz_type', 'table')
        canvas_width = data_param.get('canvas_width') or data_param.get('canvasWidth', 1200)
        canvas_height = data_param.get('canvas_height') or data_param.get('canvasHeight', 600)
        
        logger.info(f"Generating {viz_type} visualization with canvas {canvas_width}x{canvas_height}")
        
        result = generate_data_visualization(data, viz_type, canvas_width, canvas_height)
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error in generate_data_visualization endpoint: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/ai/generate-icon', methods=['POST'])
def api_generate_icon():
    """Generate an icon."""
    try:
        data = request.get_json()
        
        if not data or 'icon_name' not in data:
            return jsonify({"error": "Missing 'icon_name' parameter"}), 400
        
        icon_name = data['icon_name']
        size = data.get('size', 100)
        color = data.get('color', '#2563eb')
        
        result = generate_icon(icon_name, size, color)
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error in generate_icon endpoint: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/tools', methods=['GET'])
def list_available_tools():
    """List all available AI tools."""
    tools = [
        {
            "name": "generate_shapes",
            "description": "Generate canvas shapes from natural language request",
            "endpoint": "/generate-shapes"
        },
        {
            "name": "list_shapes",
            "description": "List all shapes on canvas",
            "endpoint": "/api/ai/list-shapes"
        },
        {
            "name": "modify_shape",
            "description": "Modify a specific shape",
            "endpoint": "/api/ai/modify-shape"
        },
        {
            "name": "delete_shape",
            "description": "Delete a shape from canvas",
            "endpoint": "/api/ai/delete-shape"
        },
        {
            "name": "arrange_shapes",
            "description": "Arrange shapes in a pattern",
            "endpoint": "/api/ai/arrange-shapes"
        },
        {
            "name": "generate_palette",
            "description": "Generate a color palette",
            "endpoint": "/api/ai/generate-palette"
        },
        {
            "name": "apply_style",
            "description": "Apply visual style to shapes",
            "endpoint": "/api/ai/apply-style"
        },
        {
            "name": "batch_modify",
            "description": "Modify multiple shapes at once",
            "endpoint": "/api/ai/batch-modify"
        },
        {
            "name": "generate_pattern",
            "description": "Generate a pattern of shapes",
            "endpoint": "/api/ai/generate-pattern"
        },
        {
            "name": "analyze_canvas",
            "description": "Analyze canvas content",
            "endpoint": "/api/ai/analyze-canvas"
        },
        {
            "name": "generate_icon",
            "description": "Generate an icon",
            "endpoint": "/api/ai/generate-icon"
        }
    ]
    return jsonify({"tools": tools}), 200


@app.route('/', methods=['GET'])
def index():
    """Home page with API documentation."""
    return jsonify({
        "service": "AI Shape Generator API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/api/health",
            "tools": "/api/tools",
            "generate_shapes": "/api/ai/generate-shapes",
            "list_shapes": "/api/ai/list-shapes",
            "modify_shape": "/api/ai/modify-shape",
            "delete_shape": "/api/ai/delete-shape",
            "arrange_shapes": "/api/ai/arrange-shapes",
            "generate_palette": "/api/ai/generate-palette",
            "apply_style": "/api/ai/apply-style",
            "batch_modify": "/api/ai/batch-modify",
            "generate_pattern": "/api/ai/generate-pattern",
            "analyze_canvas": "/api/ai/analyze-canvas",
            "generate_icon": "/api/ai/generate-icon"
        },
        "documentation": "See /api/tools for endpoint details"
    }), 200


if __name__ == '__main__':
    port = int(os.getenv('API_PORT', 5000))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Starting AI Shape Generator API on port {port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Visit http://localhost:{port} for API documentation")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
