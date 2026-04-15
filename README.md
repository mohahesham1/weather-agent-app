# Weather Agent App 🌤️

A **full-stack AI-powered weather chatbot** built with FastAPI, LangChain, and Gemini. Ask natural language questions about weather, forecasts, and air quality—the agent fetches real-time data and provides friendly, actionable advice.

---

## 📋 Project Structure

```
weather-agent-app/
├── mcp-server/                 # OpenWeatherMap API wrapper
│   ├── main.py                 # FastAPI server (port 8000)
│   ├── config.py               # Environment variables
│   ├── models.py               # Pydantic response schemas
│   ├── services.py             # Weather API functions
│   ├── requirements.txt         # Dependencies (28 packages)
│   └── .env                     # API keys (create this)
│
├── agent-backend/              # LangChain agent + chat endpoint
│   ├── main.py                 # FastAPI server (port 8001)
│   ├── agent.py                # LLM + tool calling setup
│   ├── tools.py                # @tool decorated functions
│   ├── config.py               # Environment variables
│   ├── requirements.txt         # Dependencies (61 packages)
│   └── .env                     # API keys (create this)
│
├── frontend/                   # Chat UI (plain HTML/CSS/JS)
│   ├── index.html              # Chat interface
│   ├── app.js                  # Message handling + API calls
│   ├── style.css               # Dark theme styling
│   └── .env                     # Backend URL config
│
└── README.md                   # This file
```

---

## 🏗️ Architecture

```
┌─────────────────────┐
│   Browser/Chat UI   │ (Port 3000)
│  index.html + app.js│
└──────────────┬──────┘
               │ POST /chat
               │
┌──────────────▼──────────────┐
│   Agent Backend (FastAPI)   │ (Port 8001)
│  - LangChain Agent          │
│  - Tool Calling with LLM    │
│  - Gemini (env-configurable)│
└──────────────┬──────────────┘
               │ HTTP calls
               │
┌──────────────▼──────────────┐
│   MCP Server (FastAPI)      │ (Port 8000)
│  - /weather/current         │
│  - /weather/forecast        │
│  - /weather/air-quality     │
└──────────────┬──────────────┘
               │ HTTP requests
               │
        ┌──────▼──────┐
        │ OpenWeather │
        │    API      │
        └─────────────┘
```

---

## 🚀 Quick Start

### 1️⃣ Install Dependencies

All Python packages are pre-configured in `requirements.txt`. Install them:

```bash
# Install MCP Server dependencies
cd mcp-server
pip install -r requirements.txt

# Install Agent Backend dependencies
cd ../agent-backend
pip install -r requirements.txt

# Frontend has no Python dependencies (pure HTML/CSS/JS)
```

✅ **Status**: Both `pip install` commands completed successfully!

---

### 2️⃣ Configure Environment Variables

Create `.env` files in both service directories with your API keys.

#### `mcp-server/.env`
```env
OPENWEATHER_API_KEY=your_openweathermap_api_key_here
OPENWEATHER_BASE_URL=https://api.openweathermap.org
```

Get a free API key from [OpenWeatherMap](https://openweathermap.org/api).

#### `agent-backend/.env`
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
MCP_SERVER_URL=http://localhost:8000
AGENT_TIMEOUT=30
MAX_ITERATIONS=10
```

Get a free Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).

---

### 3️⃣ Start the Services

Open **3 separate terminals** and run each service:

#### Terminal 1: MCP Server (Weather API Wrapper)
```bash
cd mcp-server
python main.py
```
**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

#### Terminal 2: Agent Backend (LangChain + LLM)
```bash
cd agent-backend
python main.py
```
**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8001
INFO:     Application startup complete
```

#### Terminal 3: Frontend Server
```bash
cd frontend
python -m http.server 3000
```
**Expected output:**
```
Serving HTTP on 0.0.0.0 port 3000 (http://0.0.0.0:3000/) ...
```

---

### 4️⃣ Open the Chat UI

Open your browser and navigate to:
```
http://localhost:3000
```

You should see a **dark-themed chat interface** with a message input box at the bottom.

---

## 💬 Example Queries

Try asking the agent natural language questions:

- **"What's the weather in London right now?"**
  - Agent calls `get_current_weather` → Returns temp, humidity, wind speed, conditions

- **"Will it rain in New York this weekend?"**
  - Agent calls `get_weather_forecast` → Returns 5-day forecast with rain probability

- **"Is the air quality good in Tokyo?"**
  - Agent calls `get_air_quality` → Returns AQI score and pollution levels

- **"I'm planning a picnic in Paris tomorrow. What should I bring?"**
  - Agent calls all 3 tools → Combines data → Gives practical advice

---

## 🛠️ Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Web Framework** | FastAPI | 0.135.3 |
| **ASGI Server** | Uvicorn | 0.44.0 |
| **LLM Framework** | LangChain | 1.2.15 |
| **LLM Core** | langchain-core | 1.2.28 |
| **Graph Execution** | LangGraph | 1.1.6 |
| **LLM Model** | Google Gemini (configured by `GEMINI_MODEL`) | `gemini-2.5-flash` default |
| **Data Validation** | Pydantic | 2.13.0 |
| **Async HTTP** | httpx | 0.28.1 |
| **Frontend** | Plain HTML/CSS/JS | ES6+ |

---

## 📁 Service Details

### MCP Server (`mcp-server/`)
Wraps the OpenWeatherMap REST API. Provides three endpoints:

1. **GET `/weather/current?city=London&units=metric`**
   - Returns: Temperature, feels like, humidity, wind speed, conditions, visibility

2. **GET `/weather/forecast?city=London&units=metric&days=5`**
   - Returns: 5-day forecast with daily min/max temps, precipitation, wind

3. **GET `/weather/air-quality?city=London`**
   - Returns: AQI score, pollution levels (PM2.5, PM10, NO₂, O₃, etc.)

### Agent Backend (`agent-backend/`)
Runs a LangChain agent with tool calling. Implements three @tool functions:

1. **`get_current_weather(city, unit)`** → Calls MCP `/weather/current`
2. **`get_weather_forecast(city, days, unit)`** → Calls MCP `/weather/forecast`
3. **`get_air_quality(city)`** → Calls MCP `/weather/air-quality`

**POST `/chat` endpoint:**
```json
{
  "message": "What's the weather in London?"
}
```

---

## Prompt Evidence (Agentic IDE)

The project was implemented in an agentic workflow using Cursor. Below are representative prompts used to generate and refine key parts of the system:

1. **MCP wrapper scaffolding**
   - "Create a FastAPI MCP wrapper for OpenWeather with `/weather/current`, `/weather/forecast`, and `/weather/air-quality` endpoints, with Pydantic models and error handling."
2. **LLM tool-calling backend**
   - "Set up LangChain/LangGraph weather agent tools that call the MCP server, then wire a `/chat` endpoint in FastAPI."
3. **Frontend integration**
   - "Build a plain HTML/CSS/JS chat UI that sends messages to backend `/chat`, shows loading state, and handles errors."
4. **Runtime debugging**
   - "Why does `python main.py` exit immediately? Add the missing FastAPI entrypoint startup so services stay running."
5. **Quality and test coverage**
   - "Create an HTTP test script with multiple input cases for MCP endpoints and optional agent chat checks."

These prompts can be shown in the video as evidence of the development approach and iterative agentic workflow.

---

## Gemini Runtime Notes

- The backend model is configurable using `GEMINI_MODEL` (default: `gemini-2.5-flash`).
- A valid `GEMINI_API_KEY` is required for `/chat`.
- Gemini API access depends on project quota/billing and model availability.
- If quota is exceeded or model access is unavailable, `/chat` may return an error message from the provider (for example HTTP 429 or 404 from Gemini API).
- Verify usage and limits at [Gemini API rate limits](https://ai.google.dev/gemini-api/docs/rate-limits).

### Frontend (`frontend/`)
Single-page chat UI with:
- Blue message bubbles (user) aligned right
- Dark gray message bubbles (agent) aligned left
- Loading indicator ("Thinking...") with animated dots
- Auto-scroll to latest message
- Error toast notifications
- Responsive design (desktop, tablet, mobile)

---

## 🔍 Debugging

### Import Errors in VS Code?
If you see "Cannot resolve import" errors in `agent.py`:
1. Press `Ctrl+Shift+P` → Search **"Python: Select Interpreter"**
2. Choose your Anaconda environment (e.g., `C:\Users\moham\anaconda3\...`)
3. Wait 10-15 seconds for Pylance to rescan

The code is correct—VS Code just needs to refresh its Python environment path.

### Services Won't Start?
- **Check port availability**: `netstat -ano | findstr :8000` (Windows) or `lsof -i :8000` (Mac/Linux)
- **Check .env files**: Ensure `OPENWEATHER_API_KEY` and `GEMINI_API_KEY` are set
- **Run `pip install -r requirements.txt`** again in each service directory

### Agent Not Calling Tools?
- Check the terminal running `agent-backend/main.py` for verbose output
- Verify MCP server is running on port 8000
- Check that `MCP_SERVER_URL=http://localhost:8000` in `.env`

---

## 📦 Dependencies Summary

**mcp-server**: 28 packages
- FastAPI, Uvicorn, Starlette, Pydantic, httpx, python-dotenv, etc.

**agent-backend**: 61 packages
- All of mcp-server + LangChain (langchain, langchain-core, langchain-google-genai, langgraph, langsmith)
- Google Gemini (google-genai, google-auth)
- Crypto & Security (cryptography, cffi, pyasn1)
- Utilities (orjson, websockets, jsonpatch, etc.)

✅ **All dependencies installed successfully** (April 14, 2026)

---

## 📝 Notes

- **No Database**: In-memory chat history (resets on server restart)
- **Single User**: Not multi-user (but can be extended)
- **API Keys Public**: .env files are in `.gitignore` (don't commit API keys!)
- **Temperature Units**: MCP supports both Celsius and Fahrenheit
- **Forecast Days**: Configurable (1-5 days supported by OpenWeather free tier)

---

## 🎯 Next Steps

1. ✅ All code implemented
2. ✅ All dependencies installed
3. ⏳ Create `.env` files with your API keys
4. ⏳ Start all three services in separate terminals
5. ⏳ Open http://localhost:3000 and chat!

---

## 📞 Support

For issues:
1. Check service logs in the terminal windows
2. Verify `.env` files have correct API keys
3. Ensure all three services are running on ports 8000, 8001, 3000
4. Check that MCP server can reach OpenWeatherMap API (network connectivity)

---

**Built with ❤️ using FastAPI, LangChain, and Google Gemini**