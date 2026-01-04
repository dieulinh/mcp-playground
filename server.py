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
        )
    ]


if __name__ == "__main__":
    # For direct testing (not in MCP mode)
    if len(sys.argv) > 1:
        request = " ".join(sys.argv[1:])
        result = generate_shapes(request)
        print(json.dumps(result, indent=2))
    else:
        print("MCP Server ready. Use 'mcp' protocol to connect.")
        print("For testing, run: python server.py 'Your shape request here'")
