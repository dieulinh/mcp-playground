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
        
        logger.info(f"Generating shapes for: {ai_request}")
        
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
            "endpoint": "/api/ai/generate-shapes"
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
