# Weather MCP Server

A Model Context Protocol (MCP) server that wraps OpenWeatherMap's REST API using FastAPI. Provides clean, developer-friendly endpoints for weather data with proper error handling and flattened response schemas.

## Features

- **Three Core Endpoints**:
  - `/weather/current` - Current weather conditions
  - `/weather/forecast` - 5-day forecast with 3-hour intervals
  - `/weather/air-quality` - Air Quality Index and components

- **Clean Architecture**:
  - Route handlers in `main.py`
  - Business logic and HTTP calls in `services.py`
  - Pydantic response models in `models.py`
  - Configuration management in `config.py`

- **Async Operations**: Uses `httpx` for non-blocking HTTP requests

- **Flattened Responses**: Transforms nested OpenWeatherMap JSON into flat, intuitive Pydantic models

- **Robust Error Handling**:
  - Proper HTTP exceptions for all failure cases
  - Comprehensive error logging
  - Graceful fallbacks

- **Security**:
  - Environment variable-based API key management
  - CORS middleware for cross-origin requests
  - No hardcoded credentials

## Setup

### Prerequisites

- Python 3.10+
- OpenWeatherMap API key (free at https://openweathermap.org/api)

### Installation

1. Create `.env` file in the `mcp-server` directory:
```bash
cp .env.example .env
# Edit .env and add your OpenWeatherMap API key
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
python main.py
# Or with auto-reload for development:
# UVICORN_RELOAD=true python main.py
```

The server will start at `http://localhost:8000`

## API Endpoints

### Health Check
```bash
GET /health
```
Returns server status.

### Current Weather
```bash
GET /weather/current?city=London
```
Returns current weather conditions for the specified city.

**Response Fields**:
- `city`: City name
- `country`: Country code
- `timestamp`: Observation time
- `weather`: Weather object with:
  - `temperature`, `feels_like`, `temp_min`, `temp_max`
  - `pressure`, `humidity`
  - `description`, `main` (weather condition)
  - `wind_speed`, `wind_gust`, `wind_direction`
  - `clouds`, `visibility`
  - `rain_1h`, `snow_1h`, `uvi` (optional)
- `sunrise`, `sunset`: Times

### 5-Day Forecast
```bash
GET /weather/forecast?city=London
```
Returns 5-day forecast with 3-hour interval predictions.

**Response Fields**:
- `city`: City name
- `country`: Country code
- `forecast_items`: Array of forecast items, each containing:
  - `timestamp`: Prediction time
  - `weather`: Same structure as current weather
- `update_time`: When forecast was generated

### Air Quality
```bash
GET /weather/air-quality?city=London
```
Returns current air quality data including AQI and component measurements.

**Response Fields**:
- `city`: City name
- `country`: Country code
- `timestamp`: Measurement time
- `aqi`: Air Quality Index object with:
  - `aqi`: 1-5 scale (1=Good, 2=Fair, 3=Moderate, 4=Poor, 5=Very Poor)
  - `description`: Human-readable description
- `components`: Pollutant concentrations (μg/m³):
  - `pm25`: PM2.5
  - `pm10`: PM10
  - `o3`: Ozone
  - `no2`: Nitrogen dioxide
  - `so2`: Sulfur dioxide
  - `co`: Carbon monoxide

## Configuration

All settings are loaded from environment variables (`.env` file):

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENWEATHER_API_KEY` | *(required)* | OpenWeatherMap API key |
| `SERVER_HOST` | `0.0.0.0` | Server bind address |
| `SERVER_PORT` | `8000` | Server port |
| `SERVER_RELOAD` | `false` | Auto-reload on file changes |
| `WEATHER_UNITS` | `metric` | Temperature units (metric/imperial/standard) |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:5173` | CORS allowed origins |

## Architecture

### Configuration (`config.py`)
- Uses Pydantic `BaseSettings` for environment variable management
- Validates required fields at startup
- Centralized configuration for the entire application

### Models (`models.py`)
- Pydantic models for all API responses
- Flattened structures for ease of use
- Comprehensive field descriptions and examples
- Includes error response model

### Services (`services.py`)
- `WeatherService` class handles all OpenWeatherMap API interactions
- Transforms nested JSON responses into flat models
- Implements error handling with proper logging
- Async methods using `httpx.AsyncClient`
- Geocoding support for air quality endpoint

### Routes (`main.py`)
- FastAPI application with lifecycle management
- Three weather endpoints with query parameter validation
- Health check endpoint
- CORS middleware for cross-origin requests
- Custom exception handlers for consistent error responses
- Request logging

## Error Handling

The server returns appropriate HTTP status codes:

| Status | Scenario |
|--------|----------|
| 200 | Successful request |
| 400 | Invalid query parameters |
| 404 | City not found |
| 502 | Invalid API response format |
| 503 | Connection to weather service failed |
| 500 | Unexpected internal error |

All error responses include:
- Human-readable error message
- Detailed error information
- HTTP status code

## Example Usage

### Using curl
```bash
# Current weather
curl "http://localhost:8000/weather/current?city=London"

# Forecast
curl "http://localhost:8000/weather/forecast?city=Tokyo"

# Air quality
curl "http://localhost:8000/weather/air-quality?city=New%20York"
```

### Using Python
```python
import httpx
import asyncio

async def get_weather():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/weather/current",
            params={"city": "London"}
        )
        return response.json()

result = asyncio.run(get_weather())
print(result)
```

### Integration with Frontend
```javascript
// Fetch current weather
const response = await fetch('/weather/current?city=London');
const data = await response.json();
console.log(`${data.city}: ${data.weather.description}`);
console.log(`Temperature: ${data.weather.temperature}°C`);
```

## Development

### Running with Auto-Reload
```bash
SERVER_RELOAD=true python main.py
```

### Viewing API Docs
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Running Tests (examples)
```bash
# Test with pytest if tests are created
pytest
```

## Logging

The server logs all requests and errors at INFO/WARNING levels. Adjust in `main.py`:
```python
logging.basicConfig(level=logging.DEBUG)  # More verbose
```

## Performance Notes

- All API calls use 10-second timeout (configurable in `config.py`)
- Async/await for non-blocking I/O
- Efficient JSON parsing with Pydantic
- CORS middleware caches origin checks

## API Key Acquisition

1. Go to https://openweathermap.org/api
2. Sign up for a free account
3. Get your API key from the dashboard
4. Add to `.env`: `OPENWEATHER_API_KEY=your_key`

Free tier includes:
- Current weather
- Forecast (5 days, 3-hour step)
- Air quality data
- ~1,000 API calls/day

## Troubleshooting

### "OPENWEATHER_API_KEY environment variable is required"
- Create `.env` file with your API key
- Ensure the key is correct and active on OpenWeatherMap

### "City not found" (404)
- Verify the city name spelling
- Try using city code (e.g., "London,GB")
- Check if city exists on OpenWeatherMap

### "Failed to connect to weather service" (503)
- Check internet connection
- Verify OpenWeatherMap API is operational
- Check if API rate limit is exceeded

## License

MIT

## Support

For issues with:
- **This MCP Server**: Check the code and logs
- **OpenWeatherMap API**: Visit https://openweathermap.org/faq
- **FastAPI**: See https://fastapi.tiangolo.com
