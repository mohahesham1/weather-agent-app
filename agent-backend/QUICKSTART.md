# Weather Agent Backend - Quick Start Guide

## Overview

This is the agent backend for the weather application. It runs a **LangChain agent powered by Gemini** (configurable via `GEMINI_MODEL`) that provides weather advice by calling three tools:

- **get_current_weather**: Get real-time weather for a city
- **get_weather_forecast**: Get a 5-day forecast
- **get_air_quality**: Get air quality and pollution data

Each tool calls our **MCP Server** (running on localhost:8000), which in turn calls OpenWeatherMap's REST API.

## Architecture

```
┌─────────────────────┐
│   Frontend (JS)     │ (port 3000, 5173, etc.)
└──────────┬──────────┘
           │ POST /chat
           ▼
┌──────────────────────────┐
│  Agent Backend (Python)  │ (port 8001)
│  - Gemini (env model)    │
│  - LangChain Agent       │
│  - 3 Tools               │
└──────────┬───────────────┘
           │ HTTP GET
           ▼
┌──────────────────────┐
│   MCP Server        │ (port 8000)
│  - /weather/current │
│  - /weather/forecast│
│  - /weather/air-quality
└──────────┬──────────┘
           │ HTTP GET
           ▼
┌──────────────────────┐
│ OpenWeatherMap API  │
└─────────────────────┘
```

## Prerequisites

1. **Python 3.8+**
2. **Gemini API Key** - Get from https://aistudio.google.com/apikey (click "Get API Key")
3. **MCP Server Running** - Must be running on localhost:8000
4. **Dependencies Installed** - Run `pip install -r requirements.txt`

## Setup

### Step 1: Create your .env file

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Then edit `.env` and add your Gemini API key:

```
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
MCP_SERVER_URL=http://localhost:8000
```

### Step 2: Start the MCP Server

In a separate terminal, go to the `mcp-server` directory and run:

```bash
cd ../mcp-server
python -m pip install -r requirements.txt  # If not already done
python main.py
```

The MCP server should now be running on `http://localhost:8000`

### Step 3: Start the Agent Backend

In the `agent-backend` directory:

```bash
python -m pip install -r requirements.txt  # If not already done
python main.py
```

The agent backend will start on `http://localhost:8001`

## Using the API

### Health Check

```bash
curl http://localhost:8001/health
```

Response:
```json
{
  "status": "healthy",
  "service": "weather-agent-backend",
  "version": "1.0.0",
  "mcp_server": "http://localhost:8000"
}
```

### Get Agent Info

```bash
curl http://localhost:8001/agent-info
```

Response includes the Gemini model, available tools, and system prompt.

### Chat with the Agent

**Single turn:**

```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Should I bring an umbrella to London tomorrow?"
  }'
```

Response:
```json
{
  "response": "Let me check the forecast for London... [Agent response with practical advice]"
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | (required) | Your Google Gemini API key |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model name to use |
| `MCP_SERVER_URL` | `http://localhost:8000` | MCP server address |
| `AGENT_TIMEOUT` | `30` | Timeout in seconds |
| `MAX_ITERATIONS` | `10` | Max agent loop iterations |

## File Structure

```
agent-backend/
├── main.py          # FastAPI app with /chat endpoint
├── agent.py         # LangChain agent setup with Gemini model from env
├── tools.py         # Three tool definitions (call MCP server)
├── config.py        # Configuration and environment loading
├── requirements.txt # Python dependencies
├── .env.example     # Example environment file
└── __init__.py
```

## How It Works

1. **User sends a message** → POST /chat endpoint
2. **Agent receives message** → Creates tool calls
3. **Tools execute** → Each tool makes an HTTP request to MCP server
4. **MCP server responds** → Returns weather data
5. **Agent processes** → Combines data and generates response
6. **Response sent back** → With advice and practical recommendations

## The Agent's Capabilities

The Gemini-based agent can:

- ✅ Understand natural language questions about weather
- ✅ Decide which tools to call based on the question
- ✅ Call **multiple tools** in one response (e.g., current weather + forecast + air quality)
- ✅ Format responses in a friendly, conversational manner
- ✅ Provide practical advice (e.g., "bring an umbrella", "avoid outdoor activities")

## Troubleshooting

### `GEMINI_API_KEY not found`
- Make sure `.env` file exists in the `agent-backend` directory
- Verify the file contains `GEMINI_API_KEY=your_key`
- Keys should be from https://aistudio.google.com/apikey

### `Connection refused to localhost:8000`
- Make sure MCP server is running: `python ../mcp-server/main.py`
- Check that it's on port 8000
- Or update `MCP_SERVER_URL` in `.env`

### `Tool execution failed`
- Check the agent logs for detailed error messages
- Verify the city name is spelled correctly
- Make sure MCP server is responding: `curl http://localhost:8000/health`

### `jsonschema validation error`
- This usually means the Gemini API key is invalid
- Get a new key from https://aistudio.google.com/apikey
- Make sure there are no extra spaces in `.env`

## Testing from Python

```python
from agent import agent_executor
from langchain_core.messages import HumanMessage

# Run a single message
result = agent_executor.invoke({
    "messages": [HumanMessage(content="What's the weather like in Tokyo?")]
})

print(result)
```

## Gemini Runtime Dependency

The `/chat` route depends on Gemini API runtime availability. If your key has no quota or the selected model is unavailable, the backend will return provider errors from Gemini (for example `429 RESOURCE_EXHAUSTED` or `404 NOT_FOUND`).

## Next Steps

1. ✅ Agent backend is set up and ready
2. 📝 Integrate with frontend (call POST http://localhost:8001/chat)
3. 🎨 Build the UI (index.html, app.js, style.css)
4. 🚀 Deploy both services to production

## Learn More

- [LangChain Docs](https://python.langchain.com/)
- [Google Gemini API](https://ai.google.dev/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
