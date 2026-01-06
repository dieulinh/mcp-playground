# Quick Start: Run AI Shape Generator

## Prerequisites
- Python 3.9+
- OpenAI API key (https://platform.openai.com/api-keys)

## 3-Step Setup

### Step 1: Install Dependencies
```bash
cd ai-shape-generator-mcp

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows

# Install packages
pip install flask flask-cors python-dotenv openai
```

### Step 2: Configure API Key
```bash
# Create or update .env file
echo "OPENAI_API_KEY=sk-your-key-here" > .env
echo "API_PORT=5000" >> .env
echo "DEBUG=True" >> .env
```

Replace `sk-your-key-here` with your real OpenAI API key from https://platform.openai.com/api-keys

### Step 3: Run the Server
```bash
source venv/bin/activate  # Make sure venv is active
python api_server.py
```

✅ You should see:
```
Starting AI Shape Generator API on port 5000
* Serving Flask app 'api_server'
* Debug mode: on
```

## Test It Works

In a **new terminal**:
```bash
curl http://localhost:5000/api/health
```

Response:
```json
{"status":"healthy","service":"AI Shape Generator API","version":"1.0.0"}
```

## Use in Frontend

1. Keep the server running (don't close the terminal)
2. In another terminal, start the frontend:
```bash
cd product-frontend
npm run dev
```

3. Open http://localhost:5173 and go to Canvas page
4. Use the AI input to generate shapes!

## Port Already in Use?

If you get "Address already in use", use a different port:
```bash
API_PORT=5001 python api_server.py
```

Then update the frontend to call `http://localhost:5001` in CanvasPage.vue

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'flask'` | Run `pip install flask flask-cors python-dotenv openai` |
| `OPENAI_API_KEY not found` | Add to .env: `OPENAI_API_KEY=sk-...` |
| `Address already in use` | Use different port: `API_PORT=5001 python api_server.py` |
| `Connection refused` | Make sure server is running with `python api_server.py` |

## Complete Setup Guide

For detailed installation instructions, see [INSTALL_AND_RUN.md](INSTALL_AND_RUN.md)

## API Documentation

Visit http://localhost:5000 when running to see full API documentation.

---

**Done! Your AI Shape Generator is ready to use! 🎨**
