# Quick Start Guide

## Files Created

```
mcp-server/
├── config.py                 # Environment variables & constants
├── models.py                 # Pydantic response schemas
├── services.py               # THREE ASYNC FUNCTIONS (core implementation)
├── main.py                   # FastAPI routes
├── requirements.txt          # Dependencies
├── .env.example              # Config template
├── README.md                 # Full documentation
├── IMPLEMENTATION.md         # Implementation details
├── SERVICES_GUIDE.md         # In-depth function guide
└── COMPLETE_SUMMARY.md       # Complete technical summary
```

## Three Async Functions in services.py

### 1️⃣ `get_current_weather(city: str)`
- **Calls**: `GET /data/2.5/weather?q={city}&appid={KEY}&units=metric`
- **Flattens**: Nested JSON → `CurrentWeatherResponse`
- **Conversions**:
  - Wind: m/s → km/h (× 3.6)
  - Visibility: meters → km (× 0.001)

### 2️⃣ `get_forecast(city: str)`
- **Calls**: `GET /data/2.5/forecast?q={city}&appid={KEY}&units=metric`
- **Groups**: 40 items (3-hour intervals) → 5 daily summaries
- **Per Day**:
  - Min/max temperature
  - Average humidity
  - Most common description
  - Average wind speed (converted m/s → km/h)
  - Rain probability (%)

### 3️⃣ `get_air_quality(city: str)`
- **Step 1**: Geocode city → lat/lon (`/geo/1.0/direct`)
- **Step 2**: Fetch AQI + pollutants (`/data/2.5/air_pollution`)
- **Mapping**: AQI 1-5 → human labels ("Good", "Fair", etc.)

## 🚀 Setup (3 Steps)

### Step 1: Configure Environment
```bash
cd mcp-server
cp .env.example .env
# Edit .env and add your OpenWeatherMap API key
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run Server
```bash
python main.py
# Server starts at http://localhost:8000
```

## 📡 API Endpoints

```bash
# Current weather
curl "http://localhost:8000/weather/current?city=London"

# 5-day forecast (daily summaries)
curl "http://localhost:8000/weather/forecast?city=London"

# Air quality index
curl "http://localhost:8000/weather/air-quality?city=London"

# Health check
curl "http://localhost:8000/health"
```

## 📊 Example Responses

### Current Weather (/weather/current?city=London)
```json
{
  "city": "London",
  "country": "GB",
  "temperature_celsius": 15.5,
  "feels_like_celsius": 14.2,
  "humidity_percent": 72,
  "description": "partly cloudy",
  "wind_speed_kmh": 18.72,           ← Converted from 5.2 m/s
  "wind_direction_degrees": 230,
  "pressure_hpa": 1013,
  "visibility_km": 10.0,              ← Converted from 10000 meters
  "clouds_percent": 50
}
```

### Forecast (/weather/forecast?city=London)
```json
{
  "city": "London",
  "country": "GB",
  "forecast": [
    {
      "date": "2025-04-14",
      "temp_min_celsius": 12.0,
      "temp_max_celsius": 16.5,
      "humidity_percent": 66,
      "description": "cloudy",
      "wind_speed_kmh": 20.48,        ← Grouped from 8 × 3-hour items
      "rain_chance_percent": 25.0
    }
    // ... 4 more days
  ]
}
```

### Air Quality (/weather/air-quality?city=London)
```json
{
  "city": "London",
  "aqi": 2,
  "aqi_label": "Fair",                ← Mapped from integer
  "pm2_5": 25.5,
  "pm10": 45.0,
  "co": 150.0,
  "no2": 32.0,
  "o3": 65.5
}
```

## 🔑 Key Implementation Details

### Unit Conversions
```python
# In services.py (line ~32-34):
MS_TO_KMH = 3.6        # 1 m/s = 3.6 km/h
METERS_TO_KM = 0.001   # 1 m = 0.001 km

# Applied in:
# - get_current_weather(): wind_speed_kmh = wind.get("speed", 0) * MS_TO_KMH
# - get_current_weather(): visibility_km = data.get("visibility", 0) * METERS_TO_KM
# - get_forecast(): wind_speed_kmh = avg_wind_speed * MS_TO_KMH
```

### AQI Label Mapping
```python
# In services.py (line ~39-45):
AQI_LABELS = {
    1: "Good",
    2: "Fair",
    3: "Moderate",
    4: "Poor",
    5: "Very Poor",
}

# Applied in get_air_quality():
aqi_label = AQI_LABELS.get(aqi_value, "Unknown")
```

### Daily Forecast Aggregation
```python
# In get_forecast() function:
# 1. Group 40 items by date → daily_forecasts dict
# 2. For each day, extract 8 3-hour items and calculate:
#    - temps = [item temps]
#    - temp_min = min(temps)
#    - temp_max = max(temps)
#    - avg_humidity = sum(humidities) / count
#    - most_common_description = mode(descriptions)
#    - avg_wind = sum(speeds) / count, then × MS_TO_KMH
#    - rain_chance = (rain_count / 8) × 100
```

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Setup, API reference, troubleshooting |
| `IMPLEMENTATION.md` | Overview, data flow, configuration |
| `SERVICES_GUIDE.md` | Detailed guide for each of 3 functions |
| `COMPLETE_SUMMARY.md` | Technical deep-dive with code snippets |

## 🔍 API Documentation

FastAPI auto-generates interactive docs:

1. **Swagger UI**: http://localhost:8000/docs
   - Try out endpoints directly
   - See request/response schemas

2. **ReDoc**: http://localhost:8000/redoc
   - Beautiful API documentation
   - Read-only reference

## ⚙️ Configuration

**Environment Variables** (`.env` file):
```env
OPENWEATHER_API_KEY=your_api_key_here
```

**Hardcoded Constants** (config.py):
```python
OPENWEATHER_BASE_URL = "https://api.openweathermap.org"
```

**CORS Allowed Origins** (main.py):
```python
CORS_ORIGINS = [
    "http://localhost:3000",   # React/Vite
    "http://localhost:5173",   # Vite default
    "http://localhost:8080",   # Alternative
]
```

## ✨ Special Features

### Async/Non-blocking
- Uses `httpx.AsyncClient()` for concurrent requests
- Multiple API calls don't block each other
- Efficient for high-concurrency scenarios

### Error Handling
- Raises `ValueError` with clear messages
- Main layer converts to HTTP 404/503 responses
- Comprehensive error logging

### Data Validation
- Pydantic models validate all responses
- Type-safe, no missing fields
- Auto-serializes to JSON

### Clean Architecture
```
Request → main.py (routes) → services.py (logic) 
→ httpx (HTTP client) → OpenWeatherMap API → Transform → Pydantic (validate) → JSON Response
```

## 🧪 Test Endpoints

```bash
# Current weather (simple)
curl "http://localhost:8000/weather/current?city=London"

# Forecast (daily summaries)
curl "http://localhost:8000/weather/forecast?city=Tokyo"

# Air quality (geocoded)
curl "http://localhost:8000/weather/air-quality?city=New%20York"

# Health check
curl "http://localhost:8000/health"
```

## 📝 OpenWeatherMap API Key

Get free key at: https://openweathermap.org/api

Free tier includes:
- Current weather
- 5-day forecast (3-hour intervals)
- Air quality data
- ~1,000 calls/day

## 🛑 Troubleshooting

| Issue | Solution |
|-------|----------|
| "OPENWEATHER_API_KEY required" | Create `.env` with API key |
| "City not found" (404) | Check city name spelling |
| "Connection failed" (503) | Check internet or API status |
| "No module named httpx" | Run `pip install -r requirements.txt` |

## 📞 Next Steps

1. ✅ Set up `.env` with API key
2. ✅ Install dependencies: `pip install -r requirements.txt`
3. ✅ Run server: `python main.py`
4. ✅ Test endpoint: `curl "http://localhost:8000/weather/current?city=London"`
5. ✅ View docs: http://localhost:8000/docs

## 🎯 Summary

✅ **3 async functions** completely implemented with:
- REST API calls using httpx
- Nested JSON → flat dictionary transformation
- Unit conversions (m/s → km/h, m → km)
- AQI integer → label mapping
- 3-hour forecast → daily summary aggregation
- Config-based API key management
- Comprehensive error handling
- Type-safe Pydantic models

Ready to integrate with your frontend! 🚀
