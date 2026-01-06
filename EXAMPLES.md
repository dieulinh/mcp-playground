#!/usr/bin/env python3
"""
Example usage of the AI Shape Generator MCP Server with all tools.
Shows how to use generate_shapes, list_shapes, modify_shape, and delete_shape tools.
"""

import json
import subprocess
from pathlib import Path

# Test cases for the MCP server
def run_test(description: str, shapes: list = None, tool_args: dict = None):
    """Helper to run a test case"""
    if shapes is None:
        shapes = []
    if tool_args is None:
        tool_args = {}
    
    print(f"\n{'='*60}")
    print(f"Test: {description}")
    print(f"{'='*60}")
    
    return shapes


# Example 1: Generate shapes
print("\n" + "="*60)
print("EXAMPLE 1: Generate Shapes")
print("="*60)
print("""
POST /api/ai/generate-shapes
{
    "request": "Add 3 red circles in the top-left corner",
    "canvasWidth": 1200,
    "canvasHeight": 600
}

Response:
{
    "shapes": [
        {"type": "circle", "x": 100, "y": 100, "radius": 30, "color": "#ff0000"},
        {"type": "circle", "x": 150, "y": 100, "radius": 30, "color": "#ff0000"},
        {"type": "circle", "x": 125, "y": 150, "radius": 30, "color": "#ff0000"}
    ]
}
""")

# Example 2: List shapes
print("\n" + "="*60)
print("EXAMPLE 2: List Shapes on Canvas")
print("="*60)
print("""
Tool: list_shapes
Input:
{
    "shapes": [
        {"type": "circle", "x": 100, "y": 100, "radius": 30, "color": "#ff0000"},
        {"type": "circle", "x": 150, "y": 100, "radius": 30, "color": "#ff0000"},
        {"type": "circle", "x": 125, "y": 150, "radius": 30, "color": "#ff0000"}
    ]
}

Response:
{
    "shapes": [...],
    "count": 3,
    "types": ["circle"]
}
""")

# Example 3: Modify shape
print("\n" + "="*60)
print("EXAMPLE 3: Modify Shape (Change Color)")
print("="*60)
print("""
Tool: modify_shape
Input:
{
    "shapes": [...],
    "shape_index": 0,
    "modifications": {
        "color": "#0000ff",
        "radius": 50
    }
}

Response:
{
    "success": true,
    "message": "Shape 0 modified successfully",
    "shapes": [...],
    "modified_shape": {"type": "circle", "x": 100, "y": 100, "radius": 50, "color": "#0000ff"}
}
""")

# Example 4: Delete shape
print("\n" + "="*60)
print("EXAMPLE 4: Delete Shape")
print("="*60)
print("""
Tool: delete_shape
Input:
{
    "shapes": [...],
    "shape_index": 1
}

Response:
{
    "success": true,
    "message": "Shape 1 deleted successfully",
    "shapes": [
        {"type": "circle", "x": 100, "y": 100, "radius": 30, "color": "#ff0000"},
        {"type": "circle", "x": 125, "y": 150, "radius": 30, "color": "#ff0000"}
    ],
    "deleted_shape": {"type": "circle", "x": 150, "y": 100, "radius": 30, "color": "#ff0000"}
}
""")

# Example 5: Complex workflow
print("\n" + "="*60)
print("EXAMPLE 5: Complex Workflow")
print("="*60)
print("""
Workflow:
1. Generate 2 blue rectangles: "Add 2 blue rectangles side by side in the center"
2. List all shapes: See what's on canvas
3. Modify first rectangle: Change color to green and make it bigger
4. Delete second rectangle: Remove it

This is how a real agent would work:
- User says: "Create 2 blue rectangles and then make one green"
- Agent uses generate_shapes to create them
- Agent uses list_shapes to confirm they're there
- Agent uses modify_shape to change one to green
- Agent returns final canvas state
""")

# Example 6: Agent-like behavior
print("\n" + "="*60)
print("EXAMPLE 6: Agent-Like Behavior")
print("="*60)
print("""
User Request: "Create a design with 3 circles, make the middle one larger, and color them red, blue, green"

Agent Steps:
1. generate_shapes("3 circles") → Creates 3 circles
2. list_shapes(shapes) → Confirms 3 circles exist at indices 0, 1, 2
3. modify_shape(shapes, 1, {"radius": 100}) → Makes middle circle larger
4. modify_shape(shapes, 0, {"color": "#ff0000"}) → First = red
5. modify_shape(shapes, 1, {"color": "#0000ff"}) → Middle = blue
6. modify_shape(shapes, 2, {"color": "#00ff00"}) → Last = green
7. Return final shapes to frontend

All in one API call!
""")

print("\n" + "="*60)
print("TESTING THE SERVER LOCALLY")
print("="*60)
print("""
To test locally, run:

cd /Users/linhnguyen/learn-django/linhlanshop/ai-shape-generator-mcp
source venv/bin/activate

# Test generate_shapes
python server.py "Add 3 red circles in the top-left corner"

# For other tools, you'll need to call them via the API endpoint
# since they require the current canvas state
""")
