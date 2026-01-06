# AI Shape Generator API Server

HTTP API wrapper for the AI Shape Generator. Provides REST endpoints for frontend applications to call AI shape generation tools.

## Quick Start

### 1. Install Dependencies

```bash
cd ai-shape-generator-mcp
pip install -r api-requirements.txt
```

### 2. Set Up Environment

Create/update `.env` file:
```
OPENAI_API_KEY=your-openai-key-here
API_PORT=5000
DEBUG=True
```

### 3. Run the API Server

```bash
python api_server.py
```

You should see:
```
Starting AI Shape Generator API on port 5000
Visit http://localhost:5000 for API documentation
```

### 4. Test the Server

**Health Check:**
```bash
curl http://localhost:5000/api/health
```

**List Tools:**
```bash
curl http://localhost:5000/api/tools
```

**Generate Shapes:**
```bash
curl -X POST http://localhost:5000/api/ai/generate-shapes \
  -H "Content-Type: application/json" \
  -d '{"request": "3 red circles in the center", "canvasWidth": 1200, "canvasHeight": 600}'
```

## Available Endpoints

### Core Tools

#### POST `/api/ai/generate-shapes`
Generate shapes from natural language.

**Request:**
```json
{
  "request": "3 blue squares in a row",
  "canvasWidth": 1200,
  "canvasHeight": 600
}
```

**Response:**
```json
{
  "shapes": [
    {"type": "rect", "x": 100, "y": 250, "width": 80, "height": 80, "color": "#0000ff"},
    {"type": "rect", "x": 250, "y": 250, "width": 80, "height": 80, "color": "#0000ff"},
    {"type": "rect", "x": 400, "y": 250, "width": 80, "height": 80, "color": "#0000ff"}
  ]
}
```

#### POST `/api/ai/list-shapes`
List all shapes on canvas.

**Request:**
```json
{
  "shapes": [...]
}
```

#### POST `/api/ai/modify-shape`
Modify a specific shape.

**Request:**
```json
{
  "shapes": [...],
  "shape_index": 0,
  "modifications": {"color": "#ff0000", "x": 200}
}
```

#### POST `/api/ai/delete-shape`
Delete a shape.

**Request:**
```json
{
  "shapes": [...],
  "shape_index": 0
}
```

### Layout Tools

#### POST `/api/ai/arrange-shapes`
Arrange shapes in a pattern.

**Request:**
```json
{
  "shapes": [...],
  "arrangement_type": "grid",
  "spacing": 20
}
```

**Arrangement Types:**
- `grid` - 3x3 grid layout
- `horizontal` - Horizontal line
- `vertical` - Vertical line
- `circle` - Circular arrangement

### Style Tools

#### POST `/api/ai/generate-palette`
Generate a color palette.

**Request:**
```json
{
  "color_scheme": "vibrant"
}
```

**Color Schemes:**
- `vibrant` - Bold colors
- `pastel` - Soft colors
- `dark` - Dark tones
- `earth` - Natural tones
- `ocean` - Blue/cyan colors
- `sunset` - Orange/red colors

#### POST `/api/ai/apply-style`
Apply visual effects to shapes.

**Request:**
```json
{
  "shapes": [...],
  "style": "shadow"
}
```

**Styles:**
- `shadow` - Drop shadow
- `outline` - Black borders
- `neon` - Glowing effect
- `glass` - Transparency
- `gradient` - Gradient fill

### Batch Operations

#### POST `/api/ai/batch-modify`
Modify multiple shapes at once.

**Request:**
```json
{
  "shapes": [...],
  "filter_type": "type:circle",
  "modifications": {"color": "#ff0000"}
}
```

**Filter Types:**
- `all` - All shapes
- `type:circle` - Only circles
- `type:rect` - Only rectangles
- `type:triangle` - Only triangles
- `color:#ff0000` - Only red shapes

### Pattern Generation

#### POST `/api/ai/generate-pattern`
Generate decorative patterns.

**Request:**
```json
{
  "pattern_type": "dots",
  "count": 12,
  "canvas_width": 1200,
  "canvas_height": 600
}
```

**Pattern Types:**
- `checkerboard` - Checkerboard pattern
- `dots` - Circular dots
- `wave` - Wave pattern
- `diagonal` - Diagonal arrangement
- `lines` - Straight lines

### Analysis

#### POST `/api/ai/analyze-canvas`
Analyze canvas content.

**Request:**
```json
{
  "shapes": [...]
}
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "total_shapes": 5,
    "shape_types": {"circle": 3, "rect": 2},
    "colors_used": ["#ff0000", "#0000ff"],
    "bounds": {
      "min_x": 50,
      "max_x": 1000,
      "min_y": 50,
      "max_y": 500
    }
  }
}
```

### Icon Generation

#### POST `/api/ai/generate-icon`
Generate vector icons.

**Request:**
```json
{
  "icon_name": "heart",
  "size": 100,
  "color": "#ff0000"
}
```

**Icons:**
- `heart` - Heart shape
- `star` - Star shape
- `arrow` - Arrow shape
- `circle` - Circle shape

## Integration with Frontend

### Vue.js Example

```javascript
const generateShapes = async (request) => {
  try {
    const response = await fetch('http://localhost:5000/api/ai/generate-shapes', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        request: request,
        canvasWidth: 1200,
        canvasHeight: 600,
      }),
    })
    
    const data = await response.json()
    if (data.shapes) {
      // Add shapes to canvas
      canvas.objects.push(...data.shapes)
    }
  } catch (error) {
    console.error('AI request failed:', error)
  }
}
```

## Running Alongside Frontend

### Terminal 1 - Django Backend
```bash
cd linhlanshop
python manage.py runserver 8000
```

### Terminal 2 - AI Shape Generator API
```bash
cd ai-shape-generator-mcp
python api_server.py
```

### Terminal 3 - Frontend (Vue.js)
```bash
cd product-frontend
npm run dev
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | required | Your OpenAI API key |
| `API_PORT` | 5000 | Port to run the API server on |
| `DEBUG` | True | Enable debug mode |

## Troubleshooting

### Connection Refused
- Make sure the API server is running: `python api_server.py`
- Check the port: Default is 5000
- Verify firewall settings allow localhost:5000

### OpenAI API Errors
- Check your `OPENAI_API_KEY` in `.env`
- Verify your API key has sufficient credits
- Check OpenAI API status page

### CORS Errors
- The API server has CORS enabled by default
- If issues persist, modify `api_server.py` CORS settings

### Invalid JSON Response
- Check the `request` parameter is valid
- Ensure OpenAI API is responding correctly
- Check logs in the terminal running the API server

## Performance Tips

1. **Caching** - Consider caching common requests
2. **Batch Operations** - Use batch_modify for multiple changes
3. **Patterns** - Generate patterns instead of individual shapes
4. **Connection Pool** - Frontend should reuse fetch connections

## Deployment

### Production Setup

1. **Use WSGI Server** (e.g., Gunicorn):
```bash
pip install gunicorn
gunicorn api_server:app -w 4 -b 0.0.0.0:5000
```

2. **Use Process Manager** (e.g., PM2):
```bash
npm install -g pm2
pm2 start api_server.py --name "ai-shapes"
pm2 save
pm2 startup
```

3. **Docker** - Create Dockerfile:
```dockerfile
FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r api-requirements.txt
CMD ["python", "api_server.py"]
```

## API Documentation

Visit `http://localhost:5000` when the server is running for full API documentation.

Visit `/api/tools` for a list of all available tools and their endpoints.

## Support

For issues or questions:
1. Check the logs: Look at the terminal output from `api_server.py`
2. Test endpoints: Use curl or Postman to test endpoints
3. Check OpenAI: Verify your API key and account status
4. Review documentation: See TOOLS_GUIDE.md for usage examples
