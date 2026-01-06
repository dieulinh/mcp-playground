#!/usr/bin/env python3
"""
MCP Server for AI-powered shape generation in canvas editor.
Generates canvas shapes based on natural language descriptions using OpenAI's GPT.
"""

import os
import json
import sys
from typing import Any
import logging
from dotenv import load_dotenv

from mcp.server import Server
from mcp.types import Tool, TextContent
from openai import OpenAI

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("ai-shape-generator")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


# System prompt for GPT to generate shapes
SYSTEM_PROMPT = """You are an expert AI assistant that converts natural language descriptions into canvas shape objects for a design application.

The user will describe shapes they want to create, and you must respond with ONLY a valid JSON object (no markdown, no extra text).

The response must have this structure:
{
  "shapes": [
    {
      "type": "circle",
      "x": 100,
      "y": 100,
      "radius": 50,
      "color": "#2563eb"
    }
  ]
}

Supported shape types and their required properties:
1. circle: type, x, y, radius, color
2. rect: type, x, y, width, height, color
3. ellipse: type, x, y, width, height, color
4. triangle: type, x, y, width, height, color
5. polygon: type, x, y, points (array of [x, y] pairs), color
6. line: type, x1, y1, x2, y2, color (optional: width, dash)
7. arrow: type, x1, y1, x2, y2, color (optional: width)
8. text: type, x, y, text, fontSize, fontFamily, color

Guidelines:
- Use hex colors (e.g., #ff0000 for red, #00ff00 for green, #0000ff for blue)
- Position shapes thoughtfully based on user description (top-left means near (0,0), center means canvas center ~(600,300))
- For "top-left", use coordinates like x: 50-150, y: 50-150
- For "center", use coordinates like x: 400-700, y: 200-400
- For "bottom-right", use coordinates like x: 800-1100, y: 400-550
- Width and height should be reasonable for the shape
- Keep radius proportional to the size described
- Always respond with valid JSON only

Example requests and expected responses:
- "Add a red circle" → {"shapes": [{"type": "circle", "x": 600, "y": 300, "radius": 50, "color": "#ff0000"}]}
- "3 blue squares in the top-left" → {"shapes": [{"type": "rect", "x": 100, "y": 100, "width": 80, "height": 80, "color": "#0000ff"}, ...]}
- "Triangle in the center" → {"shapes": [{"type": "triangle", "x": 600, "y": 300, "width": 100, "height": 100, "color": "#2563eb"}]}
"""


def generate_shapes(request: str, canvas_width: int = 1200, canvas_height: int = 600) -> dict[str, Any]:
    """
    Generate canvas shapes from a natural language request using OpenAI's GPT.
    
    Args:
        request: Natural language description of shapes to create
        canvas_width: Width of the canvas in pixels
        canvas_height: Height of the canvas in pixels
    
    Returns:
        Dictionary with "shapes" key containing list of shape objects
    """
    
    if not request.strip():
        return {"error": "Request cannot be empty"}
    
    try:
        # Add canvas dimensions to the prompt for context
        user_message = f"""Canvas dimensions: {canvas_width}x{canvas_height}

User request: {request}

Generate shapes based on this request. Remember to respond with ONLY valid JSON, no markdown or extra text."""
        
        logger.info(f"Generating shapes for request: {request}")
        
        # DEBUG: Uncomment next line to debug
        # pdb.set_trace()
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=1024,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ]
        )
        
        # Extract the response text
        response_text = response.choices[0].message.content.strip()
        
        # Parse JSON response
        shapes_data = json.loads(response_text)
        
        # Validate that response has "shapes" key
        if "shapes" not in shapes_data:
            return {"error": "Invalid response format: missing 'shapes' key"}
        
        logger.info(f"Successfully generated {len(shapes_data['shapes'])} shapes")
        return shapes_data
    
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        return {"error": f"Failed to parse AI response: {e}"}
    except Exception as e:
        logger.error(f"Error generating shapes: {e}")
        return {"error": f"Error: {str(e)}"}


def list_shapes(shapes: list[dict]) -> dict[str, Any]:
    """
    List all shapes currently on the canvas.
    
    Args:
        shapes: List of shape objects on the canvas
    
    Returns:
        Dictionary with shapes list and count
    """
    try:
        logger.info(f"Listing {len(shapes)} shapes on canvas")
        return {
            "shapes": shapes,
            "count": len(shapes),
            "types": list(set(s.get("type", "unknown") for s in shapes))
        }
    except Exception as e:
        logger.error(f"Error listing shapes: {e}")
        return {"error": f"Error: {str(e)}"}


def modify_shape(shapes: list[dict], shape_index: int, modifications: dict[str, Any]) -> dict[str, Any]:
    """
    Modify a specific shape on the canvas.
    
    Args:
        shapes: List of shape objects on the canvas
        shape_index: Index of the shape to modify (0-based)
        modifications: Dictionary of properties to modify (e.g., {"color": "#ff0000", "x": 100})
    
    Returns:
        Dictionary with modified shapes list
    """
    try:
        if not isinstance(shape_index, int) or shape_index < 0 or shape_index >= len(shapes):
            return {"error": f"Invalid shape index: {shape_index}. Canvas has {len(shapes)} shapes."}
        
        # Modify the shape
        for key, value in modifications.items():
            shapes[shape_index][key] = value
        
        logger.info(f"Modified shape at index {shape_index}: {modifications}")
        return {
            "success": True,
            "message": f"Shape {shape_index} modified successfully",
            "shapes": shapes,
            "modified_shape": shapes[shape_index]
        }
    except Exception as e:
        logger.error(f"Error modifying shape: {e}")
        return {"error": f"Error: {str(e)}"}


def delete_shape(shapes: list[dict], shape_index: int) -> dict[str, Any]:
    """
    Delete a specific shape from the canvas.
    
    Args:
        shapes: List of shape objects on the canvas
        shape_index: Index of the shape to delete (0-based)
    
    Returns:
        Dictionary with updated shapes list
    """
    try:
        if not isinstance(shape_index, int) or shape_index < 0 or shape_index >= len(shapes):
            return {"error": f"Invalid shape index: {shape_index}. Canvas has {len(shapes)} shapes."}
        
        deleted_shape = shapes.pop(shape_index)
        logger.info(f"Deleted shape at index {shape_index}: {deleted_shape}")
        
        return {
            "success": True,
            "message": f"Shape {shape_index} deleted successfully",
            "shapes": shapes,
            "deleted_shape": deleted_shape
        }
    except Exception as e:
        logger.error(f"Error deleting shape: {e}")
        return {"error": f"Error: {str(e)}"}


def arrange_shapes(shapes: list[dict], arrangement_type: str, spacing: int = 20) -> dict[str, Any]:
    """
    Arrange shapes in a specific layout pattern.
    
    Args:
        shapes: List of shape objects on the canvas
        arrangement_type: Type of arrangement ('grid', 'horizontal', 'vertical', 'circle')
        spacing: Space between shapes in pixels
    
    Returns:
        Dictionary with arranged shapes
    """
    try:
        if not shapes:
            return {"error": "No shapes to arrange"}
        
        arranged_shapes = json.loads(json.dumps(shapes))  # Deep copy
        
        if arrangement_type == 'horizontal':
            x_pos = 50
            for shape in arranged_shapes:
                shape['x'] = x_pos
                shape['y'] = 300
                x_pos += spacing + 100
        
        elif arrangement_type == 'vertical':
            y_pos = 50
            for shape in arranged_shapes:
                shape['x'] = 300
                shape['y'] = y_pos
                y_pos += spacing + 100
        
        elif arrangement_type == 'grid':
            cols = 3
            for i, shape in enumerate(arranged_shapes):
                col = i % cols
                row = i // cols
                shape['x'] = 100 + (col * (spacing + 150))
                shape['y'] = 100 + (row * (spacing + 150))
        
        elif arrangement_type == 'circle':
            import math
            center_x, center_y = 600, 300
            radius = 200
            count = len(arranged_shapes)
            for i, shape in enumerate(arranged_shapes):
                angle = (i / count) * 2 * math.pi
                shape['x'] = int(center_x + radius * math.cos(angle))
                shape['y'] = int(center_y + radius * math.sin(angle))
        
        logger.info(f"Arranged {len(arranged_shapes)} shapes in {arrangement_type} pattern")
        return {
            "success": True,
            "message": f"Shapes arranged in {arrangement_type} pattern",
            "shapes": arranged_shapes,
            "arrangement_type": arrangement_type
        }
    except Exception as e:
        logger.error(f"Error arranging shapes: {e}")
        return {"error": f"Error: {str(e)}"}


def generate_palette(color_scheme: str = 'vibrant') -> dict[str, Any]:
    """
    Generate a color palette based on a theme.
    
    Args:
        color_scheme: Type of palette ('vibrant', 'pastel', 'dark', 'earth', 'ocean', 'sunset')
    
    Returns:
        Dictionary with color palette
    """
    palettes = {
        'vibrant': ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff'],
        'pastel': ['#ffc9c9', '#c9ffcc', '#c9e1ff', '#ffffc9', '#ffc9ff', '#c9ffff'],
        'dark': ['#1a1a1a', '#333333', '#4d4d4d', '#666666', '#808080', '#999999'],
        'earth': ['#8b4513', '#a0522d', '#cd853f', '#daa520', '#d2691e', '#bc8f8f'],
        'ocean': ['#001f3f', '#003d82', '#0074d9', '#0095ff', '#7fdbca', '#4dd0e1'],
        'sunset': ['#ff6b35', '#f7931e', '#fbb034', '#ffb81c', '#f37335', '#ff5722']
    }
    
    palette = palettes.get(color_scheme, palettes['vibrant'])
    logger.info(f"Generated {color_scheme} color palette")
    
    return {
        "success": True,
        "palette": palette,
        "scheme": color_scheme,
        "color_count": len(palette)
    }


def apply_style_to_shapes(shapes: list[dict], style: str) -> dict[str, Any]:
    """
    Apply a visual style to all shapes.
    
    Args:
        shapes: List of shape objects on the canvas
        style: Style name ('shadow', 'outline', 'gradient', 'glass', 'neon')
    
    Returns:
        Dictionary with styled shapes
    """
    try:
        styled_shapes = json.loads(json.dumps(shapes))
        
        for shape in styled_shapes:
            if style == 'shadow':
                shape['shadow'] = {'offsetX': 4, 'offsetY': 4, 'blur': 8, 'color': '#00000044'}
            elif style == 'outline':
                shape['stroke'] = '#000000'
                shape['strokeWidth'] = 2
            elif style == 'neon':
                shape['shadow'] = {'offsetX': 0, 'offsetY': 0, 'blur': 20, 'color': shape.get('color', '#0000ff')}
                shape['opacity'] = 0.9
            elif style == 'glass':
                shape['opacity'] = 0.3
                shape['stroke'] = '#ffffff'
                shape['strokeWidth'] = 1
            elif style == 'gradient':
                shape['hasGradient'] = True
        
        logger.info(f"Applied {style} style to {len(styled_shapes)} shapes")
        return {
            "success": True,
            "message": f"Applied {style} style to all shapes",
            "shapes": styled_shapes,
            "style": style
        }
    except Exception as e:
        logger.error(f"Error applying style: {e}")
        return {"error": f"Error: {str(e)}"}


def batch_modify_shapes(shapes: list[dict], filter_type: str = None, modifications: dict = None) -> dict[str, Any]:
    """
    Modify multiple shapes at once based on a filter.
    
    Args:
        shapes: List of shape objects on the canvas
        filter_type: Filter type ('all', 'type:circle', 'color:#ff0000')
        modifications: Properties to modify
    
    Returns:
        Dictionary with modified shapes
    """
    try:
        modified_shapes = json.loads(json.dumps(shapes))
        modifications = modifications or {}
        count = 0
        
        for shape in modified_shapes:
            matches = False
            
            if filter_type == 'all':
                matches = True
            elif filter_type.startswith('type:'):
                shape_type = filter_type.split(':')[1]
                matches = shape.get('type') == shape_type
            elif filter_type.startswith('color:'):
                color = filter_type.split(':')[1]
                matches = shape.get('color') == color
            
            if matches:
                for key, value in modifications.items():
                    shape[key] = value
                count += 1
        
        logger.info(f"Modified {count} shapes matching filter: {filter_type}")
        return {
            "success": True,
            "message": f"Modified {count} shapes",
            "shapes": modified_shapes,
            "shapes_modified": count
        }
    except Exception as e:
        logger.error(f"Error in batch modify: {e}")
        return {"error": f"Error: {str(e)}"}


def generate_pattern(pattern_type: str, count: int = 10, canvas_width: int = 1200, canvas_height: int = 600) -> dict[str, Any]:
    """
    Generate a pattern of shapes.
    
    Args:
        pattern_type: Pattern type ('checkerboard', 'diagonal', 'dots', 'lines', 'wave')
        count: Number of elements in pattern
        canvas_width: Canvas width
        canvas_height: Canvas height
    
    Returns:
        Dictionary with pattern shapes
    """
    try:
        import math
        shapes = []
        
        if pattern_type == 'checkerboard':
            size = 50
            colors = ['#000000', '#ffffff']
            for i in range(count):
                for j in range(count):
                    shape = {
                        'type': 'rect',
                        'x': i * size,
                        'y': j * size,
                        'width': size,
                        'height': size,
                        'color': colors[(i + j) % 2]
                    }
                    shapes.append(shape)
        
        elif pattern_type == 'dots':
            for i in range(count):
                angle = (i / count) * 2 * math.pi
                x = canvas_width // 2 + 150 * math.cos(angle)
                y = canvas_height // 2 + 150 * math.sin(angle)
                shapes.append({
                    'type': 'circle',
                    'x': int(x),
                    'y': int(y),
                    'radius': 10,
                    'color': f'#{(i * 255 // count):02x}0000'
                })
        
        elif pattern_type == 'wave':
            for i in range(count):
                x = (i / count) * canvas_width
                y = canvas_height // 2 + 50 * math.sin((i / count) * 2 * math.pi)
                shapes.append({
                    'type': 'circle',
                    'x': int(x),
                    'y': int(y),
                    'radius': 8,
                    'color': '#2563eb'
                })
        
        logger.info(f"Generated {pattern_type} pattern with {len(shapes)} elements")
        return {
            "success": True,
            "message": f"Generated {pattern_type} pattern",
            "shapes": shapes,
            "pattern_type": pattern_type,
            "element_count": len(shapes)
        }
    except Exception as e:
        logger.error(f"Error generating pattern: {e}")
        return {"error": f"Error: {str(e)}"}


def analyze_canvas(shapes: list[dict]) -> dict[str, Any]:
    """
    Analyze the current canvas content.
    
    Args:
        shapes: List of shape objects on the canvas
    
    Returns:
        Dictionary with canvas analysis
    """
    try:
        analysis = {
            "total_shapes": len(shapes),
            "shape_types": {},
            "colors_used": [],
            "canvas_coverage": 0,
            "bounds": {}
        }
        
        if not shapes:
            return analysis
        
        # Count shape types
        for shape in shapes:
            shape_type = shape.get('type', 'unknown')
            analysis['shape_types'][shape_type] = analysis['shape_types'].get(shape_type, 0) + 1
            
            # Collect colors
            color = shape.get('color')
            if color and color not in analysis['colors_used']:
                analysis['colors_used'].append(color)
        
        # Calculate bounds
        xs = [s.get('x', 0) for s in shapes]
        ys = [s.get('y', 0) for s in shapes]
        analysis['bounds'] = {
            'min_x': min(xs),
            'max_x': max(xs),
            'min_y': min(ys),
            'max_y': max(ys)
        }
        
        logger.info(f"Canvas analysis: {analysis['total_shapes']} shapes, {len(analysis['colors_used'])} colors")
        return {
            "success": True,
            "analysis": analysis
        }
    except Exception as e:
        logger.error(f"Error analyzing canvas: {e}")
        return {"error": f"Error: {str(e)}"}


def generate_icon(icon_name: str, size: int = 100, color: str = '#2563eb') -> dict[str, Any]:
    """
    Generate a simple icon from a name.
    
    Args:
        icon_name: Name of icon to generate (heart, star, arrow, etc.)
        size: Size of icon
        color: Icon color
    
    Returns:
        Dictionary with icon shapes
    """
    try:
        icons = {
            'heart': [
                {'type': 'circle', 'x': 0, 'y': 10, 'radius': 15, 'color': color},
                {'type': 'circle', 'x': 30, 'y': 10, 'radius': 15, 'color': color},
                {'type': 'polygon', 'x': 15, 'y': 20, 'points': [[0, 0], [30, 0], [15, 30]], 'color': color}
            ],
            'star': [
                {'type': 'polygon', 'x': 25, 'y': 5, 'points': [[0, 15], [5, 25], [15, 25], [8, 35], [12, 45], [0, 37], [-12, 45], [-8, 35], [-15, 25], [-5, 25]], 'color': color}
            ],
            'arrow': [
                {'type': 'line', 'x1': 0, 'y1': 25, 'x2': 40, 'y2': 25, 'color': color, 'width': 3},
                {'type': 'line', 'x1': 40, 'y1': 25, 'x2': 30, 'y2': 15, 'color': color, 'width': 3},
                {'type': 'line', 'x1': 40, 'y1': 25, 'x2': 30, 'y2': 35, 'color': color, 'width': 3}
            ],
            'circle': [
                {'type': 'circle', 'x': 25, 'y': 25, 'radius': 25, 'color': color}
            ]
        }
        
        icon_shapes = icons.get(icon_name, icons['circle'])
        logger.info(f"Generated {icon_name} icon")
        
        return {
            "success": True,
            "icon_name": icon_name,
            "shapes": icon_shapes,
            "size": size,
            "color": color
        }
    except Exception as e:
        logger.error(f"Error generating icon: {e}")
        return {"error": f"Error: {str(e)}"}


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> dict:
    """Handle tool calls from the MCP protocol."""
    
    if name == "generate_shapes":
        request = arguments.get("request", "")
        canvas_width = arguments.get("canvas_width", 1200)
        canvas_height = arguments.get("canvas_height", 600)
        
        result = generate_shapes(request, canvas_width, canvas_height)
        
        return {
            "content": [{"type": "text", "text": json.dumps(result)}],
            "is_error": "error" in result
        }
    
    elif name == "list_shapes":
        shapes = arguments.get("shapes", [])
        result = list_shapes(shapes)
        
        return {
            "content": [{"type": "text", "text": json.dumps(result)}],
            "is_error": "error" in result
        }
    
    elif name == "modify_shape":
        shapes = arguments.get("shapes", [])
        shape_index = arguments.get("shape_index", -1)
        modifications = arguments.get("modifications", {})
        
        result = modify_shape(shapes, shape_index, modifications)
        
        return {
            "content": [{"type": "text", "text": json.dumps(result)}],
            "is_error": "error" in result
        }
    
    elif name == "delete_shape":
        shapes = arguments.get("shapes", [])
        shape_index = arguments.get("shape_index", -1)
        
        result = delete_shape(shapes, shape_index)
        
        return {
            "content": [{"type": "text", "text": json.dumps(result)}],
            "is_error": "error" in result
        }
    
    elif name == "arrange_shapes":
        shapes = arguments.get("shapes", [])
        arrangement_type = arguments.get("arrangement_type", "grid")
        spacing = arguments.get("spacing", 20)
        
        result = arrange_shapes(shapes, arrangement_type, spacing)
        
        return {
            "content": [{"type": "text", "text": json.dumps(result)}],
            "is_error": "error" in result
        }
    
    elif name == "generate_palette":
        color_scheme = arguments.get("color_scheme", "vibrant")
        
        result = generate_palette(color_scheme)
        
        return {
            "content": [{"type": "text", "text": json.dumps(result)}],
            "is_error": False
        }
    
    elif name == "apply_style_to_shapes":
        shapes = arguments.get("shapes", [])
        style = arguments.get("style", "shadow")
        
        result = apply_style_to_shapes(shapes, style)
        
        return {
            "content": [{"type": "text", "text": json.dumps(result)}],
            "is_error": "error" in result
        }
    
    elif name == "batch_modify_shapes":
        shapes = arguments.get("shapes", [])
        filter_type = arguments.get("filter_type", "all")
        modifications = arguments.get("modifications", {})
        
        result = batch_modify_shapes(shapes, filter_type, modifications)
        
        return {
            "content": [{"type": "text", "text": json.dumps(result)}],
            "is_error": "error" in result
        }
    
    elif name == "generate_pattern":
        pattern_type = arguments.get("pattern_type", "dots")
        count = arguments.get("count", 10)
        canvas_width = arguments.get("canvas_width", 1200)
        canvas_height = arguments.get("canvas_height", 600)
        
        result = generate_pattern(pattern_type, count, canvas_width, canvas_height)
        
        return {
            "content": [{"type": "text", "text": json.dumps(result)}],
            "is_error": "error" in result
        }
    
    elif name == "analyze_canvas":
        shapes = arguments.get("shapes", [])
        
        result = analyze_canvas(shapes)
        
        return {
            "content": [{"type": "text", "text": json.dumps(result)}],
            "is_error": "error" in result
        }
    
    elif name == "generate_icon":
        icon_name = arguments.get("icon_name", "circle")
        size = arguments.get("size", 100)
        color = arguments.get("color", "#2563eb")
        
        result = generate_icon(icon_name, size, color)
        
        return {
            "content": [{"type": "text", "text": json.dumps(result)}],
            "is_error": "error" in result
        }
    
    return {
        "content": [{"type": "text", "text": f"Unknown tool: {name}"}],
        "is_error": True
    }


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        # Core Shape Tools
        Tool(
            name="generate_shapes",
            description="Generate canvas shapes from natural language description. Takes a user request like 'Add 3 red circles in the top-left' and returns structured shape objects.",
            inputSchema={
                "type": "object",
                "properties": {
                    "request": {
                        "type": "string",
                        "description": "Natural language description of shapes to create (e.g., 'Add 3 red circles in the top-left corner')"
                    },
                    "canvas_width": {
                        "type": "integer",
                        "description": "Canvas width in pixels (default: 1200)",
                        "default": 1200
                    },
                    "canvas_height": {
                        "type": "integer",
                        "description": "Canvas height in pixels (default: 600)",
                        "default": 600
                    }
                },
                "required": ["request"]
            }
        ),
        Tool(
            name="list_shapes",
            description="List all shapes currently on the canvas.",
            inputSchema={
                "type": "object",
                "properties": {
                    "shapes": {
                        "type": "array",
                        "description": "Current list of shapes on the canvas",
                        "default": []
                    }
                },
                "required": ["shapes"]
            }
        ),
        Tool(
            name="modify_shape",
            description="Modify properties of an existing shape on the canvas (e.g., color, size, position).",
            inputSchema={
                "type": "object",
                "properties": {
                    "shapes": {
                        "type": "array",
                        "description": "Current list of shapes on the canvas"
                    },
                    "shape_index": {
                        "type": "integer",
                        "description": "Index of the shape to modify (0-based)"
                    },
                    "modifications": {
                        "type": "object",
                        "description": "Properties to modify (e.g., {'color': '#ff0000', 'x': 100})"
                    }
                },
                "required": ["shapes", "shape_index", "modifications"]
            }
        ),
        Tool(
            name="delete_shape",
            description="Delete a specific shape from the canvas.",
            inputSchema={
                "type": "object",
                "properties": {
                    "shapes": {
                        "type": "array",
                        "description": "Current list of shapes on the canvas"
                    },
                    "shape_index": {
                        "type": "integer",
                        "description": "Index of the shape to delete (0-based)"
                    }
                },
                "required": ["shapes", "shape_index"]
            }
        ),
        
        # Layout & Arrangement Tools
        Tool(
            name="arrange_shapes",
            description="Arrange shapes in organized layout patterns (grid, horizontal, vertical, or circle).",
            inputSchema={
                "type": "object",
                "properties": {
                    "shapes": {
                        "type": "array",
                        "description": "Current list of shapes on the canvas"
                    },
                    "arrangement_type": {
                        "type": "string",
                        "enum": ["grid", "horizontal", "vertical", "circle"],
                        "description": "Type of arrangement pattern"
                    },
                    "spacing": {
                        "type": "integer",
                        "description": "Space between shapes in pixels (default: 20)",
                        "default": 20
                    }
                },
                "required": ["shapes", "arrangement_type"]
            }
        ),
        
        # Color & Style Tools
        Tool(
            name="generate_palette",
            description="Generate a color palette based on a theme or style.",
            inputSchema={
                "type": "object",
                "properties": {
                    "color_scheme": {
                        "type": "string",
                        "enum": ["vibrant", "pastel", "dark", "earth", "ocean", "sunset"],
                        "description": "Color palette theme"
                    }
                },
                "required": ["color_scheme"]
            }
        ),
        Tool(
            name="apply_style_to_shapes",
            description="Apply visual styles to all shapes on the canvas (shadow, outline, neon, glass, gradient).",
            inputSchema={
                "type": "object",
                "properties": {
                    "shapes": {
                        "type": "array",
                        "description": "Current list of shapes on the canvas"
                    },
                    "style": {
                        "type": "string",
                        "enum": ["shadow", "outline", "neon", "glass", "gradient"],
                        "description": "Visual style to apply"
                    }
                },
                "required": ["shapes", "style"]
            }
        ),
        
        # Batch Operations
        Tool(
            name="batch_modify_shapes",
            description="Modify multiple shapes at once based on filter criteria (all shapes, by type, or by color).",
            inputSchema={
                "type": "object",
                "properties": {
                    "shapes": {
                        "type": "array",
                        "description": "Current list of shapes on the canvas"
                    },
                    "filter_type": {
                        "type": "string",
                        "description": "Filter criteria: 'all', 'type:circle', 'type:rect', 'color:#ff0000', etc."
                    },
                    "modifications": {
                        "type": "object",
                        "description": "Properties to modify for all matching shapes"
                    }
                },
                "required": ["shapes", "filter_type", "modifications"]
            }
        ),
        
        # Pattern Generation
        Tool(
            name="generate_pattern",
            description="Generate decorative patterns on the canvas (checkerboard, dots, wave, etc.).",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern_type": {
                        "type": "string",
                        "enum": ["checkerboard", "diagonal", "dots", "lines", "wave"],
                        "description": "Type of pattern to generate"
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of elements in pattern (default: 10)",
                        "default": 10
                    },
                    "canvas_width": {
                        "type": "integer",
                        "description": "Canvas width in pixels (default: 1200)",
                        "default": 1200
                    },
                    "canvas_height": {
                        "type": "integer",
                        "description": "Canvas height in pixels (default: 600)",
                        "default": 600
                    }
                },
                "required": ["pattern_type"]
            }
        ),
        
        # Analysis Tools
        Tool(
            name="analyze_canvas",
            description="Analyze the current canvas content and provide statistics (shape count, types, colors, bounds).",
            inputSchema={
                "type": "object",
                "properties": {
                    "shapes": {
                        "type": "array",
                        "description": "Current list of shapes on the canvas"
                    }
                },
                "required": ["shapes"]
            }
        ),
        
        # Icon Generation
        Tool(
            name="generate_icon",
            description="Generate simple vector icons (heart, star, arrow, circle, etc.).",
            inputSchema={
                "type": "object",
                "properties": {
                    "icon_name": {
                        "type": "string",
                        "enum": ["heart", "star", "arrow", "circle"],
                        "description": "Name of icon to generate"
                    },
                    "size": {
                        "type": "integer",
                        "description": "Icon size (default: 100)",
                        "default": 100
                    },
                    "color": {
                        "type": "string",
                        "description": "Icon color in hex format (default: #2563eb)",
                        "default": "#2563eb"
                    }
                },
                "required": ["icon_name"]
            }
        )
    ]


if __name__ == "__main__":
    # For direct testing (not in MCP mode)
    # Usage: python server.py "request" [output_file.json]
    if len(sys.argv) > 1:
        request = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else "results.json"
        
        result = generate_shapes(request)
        
        # Print to stdout
        print(json.dumps(result, indent=2))
        
        # Save to file with canvas structure
        try:
            # Extract shapes from the result
            shapes = result.get("shapes", []) if "error" not in result else []
            
            # Add rotation property to each shape (default 0)
            for shape in shapes:
                if "rotation" not in shape:
                    shape["rotation"] = 0
            
            # Create canvas structure compatible with frontend
            canvas_data = {
                "id": 1,
                "name": "Canvas 1",
                "width": 1200,
                "height": 600,
                "objects": shapes,
                "undoHistory": []
            }
            
            with open(output_file, "w") as f:
                json.dump(canvas_data, f, indent=2)
            print(f"\n✅ Results saved to {output_file}", file=sys.stderr)
        except Exception as e:
            print(f"⚠️ Could not save to file: {e}", file=sys.stderr)
    else:
        print("MCP Server ready. Use 'mcp' protocol to connect.")
        print("\nUsage for testing:")
        print("  python server.py 'Your shape request here'")
        print("  python server.py 'Your request' output_filename.json")
        print("\nResults will be printed to stdout and saved to a JSON file")
