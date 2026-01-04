# AI Shape Generator MCP Server

A Model Context Protocol (MCP) server that generates canvas shapes from natural language descriptions using OpenAI's GPT models.

## Setup

### Prerequisites
- Python 3.9+
- OpenAI API key (get one at https://platform.openai.com/api-keys)

### Installation

1. **Navigate to the directory:**
```bash
cd ai-shape-generator-mcp
```

2. **Create virtual environment (if not already done):**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -e .
```

4. **Set up environment variables:**
```bash
# Create a .env file in this directory
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

Or export it:
```bash
export OPENAI_API_KEY="your_api_key_here"
```

## Usage

### Direct Testing
```bash
python server.py "Add 3 red circles in the top-left corner"
```

### In Django View
See the integration guide below.

## MCP Server Details

### Tool: `generate_shapes`

**Input:**
- `request` (string, required): Natural language description of shapes
  - Example: "Add 3 red circles in the top-left"
  - Example: "Create a blue triangle in the center"
- `canvas_width` (integer, optional): Canvas width in pixels (default: 1200)
- `canvas_height` (integer, optional): Canvas height in pixels (default: 600)

**Output:**
```json
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
```

### Supported Shape Types

1. **circle**: `type, x, y, radius, color`
2. **rect**: `type, x, y, width, height, color`
3. **ellipse**: `type, x, y, width, height, color`
4. **triangle**: `type, x, y, width, height, color`
5. **polygon**: `type, x, y, points (array), color`
6. **line**: `type, x1, y1, x2, y2, color`
7. **arrow**: `type, x1, y1, x2, y2, color`
8. **text**: `type, x, y, text, fontSize, fontFamily, color`

## Django Integration

Add this to your Django views:

```python
import json
import subprocess
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["POST"])
def generate_shapes(request):
    """API endpoint for AI shape generation."""
    try:
        data = json.loads(request.body)
        user_request = data.get('request', '')
        canvas_width = data.get('canvasWidth', 1200)
        canvas_height = data.get('canvasHeight', 600)
        
        # Call the MCP server
        result = subprocess.run(
            ['python', 'ai-shape-generator-mcp/server.py', user_request],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            shapes_data = json.loads(result.stdout)
            return JsonResponse(shapes_data)
        else:
            return JsonResponse(
                {'error': result.stderr},
                status=400
            )
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
```

Then add to `urls.py`:
```python
path('api/ai/generate-shapes', generate_shapes, name='generate_shapes'),
```

## Architecture

```
Frontend (Vue.js)
    ↓ POST /api/ai/generate-shapes
Django Backend
    ↓ subprocess call
MCP Server (Python)
    ↓ Claude API
Anthropic API
    ↓ JSON response
MCP Server
    ↓ return JSON
Django Backend
    ↓ return to frontend
Frontend (renders shapes)
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'mcp'"
Make sure you've installed dependencies:
```bash
pip install -e .
```

### "ANTHROPIC_API_KEY not found"
Set your API key:
```bash
export ANTHROPIC_API_KEY="your_key_here"
```

### "Invalid response format"
Claude may have returned invalid JSON. Check the logs for details.

## Development

### Install dev dependencies:
```bash
pip install -e ".[dev]"
```

### Run tests:
```bash
pytest
```

### Format code:
```bash
black server.py
ruff check server.py
```

## License

MIT
