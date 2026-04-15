# Weather Agent - Complete Deployment Guide

This guide shows how to run the entire Weather Agent application locally.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     User Browser                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Frontend (Plain HTML/CSS/JS)                           │ │
│  │  - Chat UI on http://localhost:3000                     │ │
│  │  - Sends POST /chat requests                            │ │
│  └──────────────────────┬──────────────────────────────────┘ │
└─────────────────────────┼─────────────────────────────────────┘
                          │ HTTP POST /chat
┌─────────────────────────▼─────────────────────────────────────┐
│              Agent Backend (Python FastAPI)                    │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  - Server on http://localhost:8001                       │ │
│  │  - Gemini LLM (configurable via GEMINI_MODEL)            │ │
│  │  - LangChain Agent with Tool Calling                     │ │
│  │  - Three @tool decorated functions                       │ │
│  └────────────────────────┬─────────────────────────────────┘ │
│  ┌────────────────────────▼─────────────────────────────────┐ │
│  │  Tools: get_current_weather, get_weather_forecast,       │ │
│  │         get_air_quality                                  │ │
│  │  All call: http://localhost:8000 (MCP Server)            │ │
│  └────────────────────────┬─────────────────────────────────┘ │
└─────────────────────────┬─────────────────────────────────────┘
                          │ HTTP GET /weather/*
┌─────────────────────────▼─────────────────────────────────────┐
│              MCP Server (Python FastAPI)                       │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  - Server on http://localhost:8000                       │ │
│  │  - Three endpoints:                                      │ │
│  │    • GET /weather/current                                │ │
│  │    • GET /weather/forecast                               │ │
│  │    • GET /weather/air-quality                            │ │
│  └────────────────────────┬─────────────────────────────────┘ │
└─────────────────────────┬─────────────────────────────────────┘
                          │ HTTP GET (calls OpenWeatherMap)
┌─────────────────────────▼─────────────────────────────────────┐
│              OpenWeatherMap REST API                           │
│  https://api.openweathermap.org/data/X.X/...                 │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

- Python 3.8+
- pip package manager
- OpenWeatherMap API Key (sign up free at https://openweathermap.org/api)
- Google Gemini API Key (get from https://aistudio.google.com/apikey)
- A terminal/command line

## Step-by-Step Setup

### 1. Clone or Download the Project

```bash
cd weather-agent-app
```

Project structure:
```
weather-agent-app/
├── mcp-server/           # Weather data server
│   ├── main.py
│   ├── config.py
│   ├── services.py
│   ├── models.py
│   ├── requirements.txt
│   └── QUICKSTART.md
├── agent-backend/        # LangChain weather agent
│   ├── main.py
│   ├── agent.py
│   ├── tools.py
│   ├── config.py
│   ├── requirements.txt
│   ├── .env.example
│   └── QUICKSTART.md
└── frontend/             # Chat UI
    ├── index.html
    ├── app.js
    ├── style.css
    └── README.md
```

### 2. Set Up MCP Server (Terminal 1)

```bash
# Navigate to mcp-server
cd mcp-server

# Install dependencies
pip install -r requirements.txt

# Create .env file if not exists
# Add your OpenWeatherMap API key:
# OPENWEATHER_API_KEY=your_actual_key_here

# Start the server
python main.py
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

Server is now running on **http://localhost:8000**

### 3. Set Up Agent Backend (Terminal 2)

```bash
# Navigate to agent-backend
cd agent-backend

# Install dependencies
pip install -r requirements.txt

# Create .env file from template
cp .env.example .env

# Edit .env and add your keys
# GEMINI_API_KEY=your_actual_gemini_key_here
# MCP_SERVER_URL=http://localhost:8000
```

Then start the agent backend:

```bash
python main.py
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8001
Starting Weather Agent Backend on http://localhost:8001
```

Server is now running on **http://localhost:8001**

### 4. Start the Frontend (Terminal 3)

#### Option A: Open directly in browser
```bash
# macOS
open frontend/index.html

# Windows
start frontend/index.html

# Linux
firefox frontend/index.html
```

#### Option B: Use Python HTTP server (recommended)
```bash
# Navigate to project root
cd weather-agent-app

# Start server on port 3000
python -m http.server 3000 --directory frontend
```

Then visit: **http://localhost:3000**

## Verification Checklist

✅ **MCP Server (Port 8000)**
```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy", ...}
```

✅ **Agent Backend (Port 8001)**
```bash
curl http://localhost:8001/health
# Should return: {"status": "healthy", ...}
```

✅ **Frontend**
- Open http://localhost:3000 in browser
- Should see dark chat interface
- Try typing a message

## Testing the Full Flow

### Test from Browser

1. Open http://localhost:3000 (or localhost:8000 if using direct HTML file)
2. Type: "What's the weather in London?"
3. Should see:
   - Message displayed as blue bubble (right side)
   - "Thinking..." loading indicator (left side)
   - Agent response about London weather (left side)
   - Auto-scroll to show latest message

### Test from Command Line

```bash
# Test MCP Server directly
curl "http://localhost:8000/weather/current?city=London"
curl "http://localhost:8000/weather/forecast?city=London"
curl "http://localhost:8000/weather/air-quality?city=London"

# Test Agent Backend
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the weather in Paris?"}'
```

### Gemini Quota and Model Access

The `/chat` endpoint depends on Google Gemini runtime access. Make sure:

1. `GEMINI_API_KEY` is valid.
2. `GEMINI_MODEL` is set to an available model (default is `gemini-2.5-flash`).
3. The Google project has available quota/billing for the selected model.

If not, chat requests can fail with provider errors such as `429 RESOURCE_EXHAUSTED` (quota exceeded) or `404 NOT_FOUND` (model unavailable to project).

## Troubleshooting

### "Connection refused" to MCP Server
**Problem**: Agent backend can't reach MCP server on port 8000
**Solution**:
1. Make sure MCP server is running: `python mcp-server/main.py`
2. Check firewall isn't blocking localhost:8000
3. Verify `MCP_SERVER_URL` in agent-backend `.env` is correct

### "GEMINI_API_KEY not found"
**Problem**: Agent backend missing API key
**Solution**:
1. Create `agent-backend/.env` file
2. Get key from https://aistudio.google.com/apikey
3. Add: `GEMINI_API_KEY=your_actual_key_here`

### "OPENWEATHER_API_KEY not found"
**Problem**: MCP server missing API key
**Solution**:
1. Sign up for free at https://openweathermap.org/api
2. Get your API key from dashboard
3. Add to `mcp-server/.env`: `OPENWEATHER_API_KEY=your_key_here`

### Frontend showing old UI
**Problem**: Browser cached old files
**Solution**:
1. Hard refresh: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
2. Open DevTools, go to Network tab, disable cache
3. Clear browser cache

### Messages not sending
**Problem**: Frontend not connecting to backend
**Solution**:
1. Check browser console (F12) for error messages
2. Verify agent-backend is running on port 8001
3. Check CORS settings in agent-backend/main.py

### Loading spinning forever
**Problem**: Backend timeout or agent not responding
**Solution**:
1. Check agent-backend terminal for errors
2. Could be slow MCP server or network issue
3. Check if OpenWeatherMap API is responding: `curl https://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_KEY`

## Port Requirements

Make sure these ports are available:

| Service | Port | URL |
|---------|------|-----|
| MCP Server | 8000 | http://localhost:8000 |
| Agent Backend | 8001 | http://localhost:8001 |
| Frontend (optional) | 3000 | http://localhost:3000 |

If ports are in use, you can change them in the respective `main.py` files:

```python
# Change port in uvicorn.run()
uvicorn.run("main:app", host="0.0.0.0", port=9000)  # Changed from 8000/8001
```

## Performance Tips

1. **Keep terminal windows visible** - Easy to spot errors
2. **Use `--reload` flag** for development:
   ```bash
   python main.py --reload  # Auto-reloads on file changes
   ```
3. **Monitor logs** - Check terminal output for backend errors
4. **Use DevTools** - Check Network tab for slow requests

## Environment Variables

### MCP Server (mcp-server/.env)
```
OPENWEATHER_API_KEY=your_api_key
OPENWEATHER_BASE_URL=https://api.openweathermap.org
```

### Agent Backend (agent-backend/.env)
```
GEMINI_API_KEY=your_api_key
MCP_SERVER_URL=http://localhost:8000
AGENT_TIMEOUT=30
MAX_ITERATIONS=10
```

## Next Steps

1. ✅ Getting started - You did it!
2. 📝 Customize the UI - Edit `frontend/style.css` for colors/fonts
3. 🔧 Add features - Persistent storage, voice input, weather icons
4. 🚀 Deploy to cloud - Deploy to AWS, Azure, or Heroku
5. 🔐 Add authentication - Protect your endpoints

## Common Tasks

### Restart everything
```bash
# Kill all servers (Ctrl+C in each terminal)
# Restart in this order:
1. mcp-server/main.py
2. agent-backend/main.py
3. frontend (browser or HTTP server)
```

### View chat history
```javascript
// Open browser DevTools (F12) and paste:
chatDebug.getHistory()
```

### Clear chat
```javascript
// Browser DevTools:
chatDebug.clearHistory()
```

### Check backend status
```bash
# Terminal:
curl http://localhost:8001/health
curl http://localhost:8000/health
```

## Support

For issues:
1. Check terminal output for error messages
2. Look at browser console (F12) for frontend errors  
3. Try restarting servers
4. Verify API keys are set correctly
5. Check internet connection

## Summary

**You now have:**
- 🌡️ MCP Server on localhost:8000 (weather data fetcher)
- 🤖 Agent Backend on localhost:8001 (LangChain agent)
- 💬 Frontend Chat UI on localhost:3000 (browser interface)

**The flow:**
User → Browser Chat → Backend Agent → MCP Server → OpenWeatherMap API

**All working together to answer weather questions!** ⛅
