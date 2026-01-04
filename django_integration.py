"""
Django integration for AI Shape Generator MCP Server.

Add this to your Django app's views.py
"""

import json
import subprocess
import os
from pathlib import Path
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


# Path to the MCP server
MCP_SERVER_PATH = Path(__file__).resolve().parent.parent.parent / 'ai-shape-generator-mcp' / 'server.py'


@require_http_methods(["POST"])
def generate_shapes(request):
    """
    API endpoint for AI shape generation.
    
    Expected POST data:
    {
        "request": "Add 3 red circles in the top-left",
        "canvasWidth": 1200,
        "canvasHeight": 600
    }
    
    Returns:
    {
        "shapes": [
            {
                "type": "circle",
                "x": 100,
                "y": 100,
                "radius": 50,
                "color": "#ff0000"
            }
        ]
    }
    """
    try:
        # Parse request
        data = json.loads(request.body)
        user_request = data.get('request', '').strip()
        canvas_width = data.get('canvasWidth', 1200)
        canvas_height = data.get('canvasHeight', 600)
        
        # Validate input
        if not user_request:
            return JsonResponse(
                {'error': 'Request cannot be empty'},
                status=400
            )
        
        # Get API key from environment
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            return JsonResponse(
                {'error': 'OPENAI_API_KEY not configured'},
                status=500
            )
        
        # Prepare environment with API key
        env = os.environ.copy()
        env['OPENAI_API_KEY'] = api_key
        
        # Call the MCP server as a subprocess
        result = subprocess.run(
            ['python', str(MCP_SERVER_PATH), user_request],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
            cwd=str(MCP_SERVER_PATH.parent)
        )
        
        # Check if the subprocess was successful
        if result.returncode != 0:
            error_msg = result.stderr or 'Unknown error'
            return JsonResponse(
                {'error': f'Shape generation failed: {error_msg}'},
                status=400
            )
        
        # Parse the JSON response
        try:
            shapes_data = json.loads(result.stdout)
        except json.JSONDecodeError:
            return JsonResponse(
                {'error': 'Invalid response format from shape generator'},
                status=400
            )
        
        # Check for errors in the response
        if 'error' in shapes_data:
            return JsonResponse(
                {'error': shapes_data['error']},
                status=400
            )
        
        # Return the generated shapes
        return JsonResponse(shapes_data)
    
    except subprocess.TimeoutExpired:
        return JsonResponse(
            {'error': 'Shape generation timed out'},
            status=408
        )
    except json.JSONDecodeError:
        return JsonResponse(
            {'error': 'Invalid request format'},
            status=400
        )
    except Exception as e:
        return JsonResponse(
            {'error': f'Unexpected error: {str(e)}'},
            status=500
        )
