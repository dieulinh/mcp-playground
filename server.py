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
import pdb

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
    pdb.set_trace()
    
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
    
    return {
        "content": [{"type": "text", "text": f"Unknown tool: {name}"}],
        "is_error": True
    }


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
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
