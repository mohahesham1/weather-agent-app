# Services Implementation Guide

## Overview

This document explains the three async functions in `services.py` that handle all OpenWeatherMap API interactions and data transformations.

## Architecture

```
FastAPI Route Handlers (main.py)
    ↓
JSON Response Validation (Pydantic Models in models.py)
    ↓
Business Logic Layer (services.py - THREE ASYNC FUNCTIONS)
    ↓
External API (OpenWeatherMap REST API)
```

## Three Core Functions

### 1. `get_current_weather(city: str) → CurrentWeatherResponse`

**What it does:**
- Calls OpenWeatherMap's `/data/2.5/weather` endpoint
- Transforms nested JSON response into flat fields
- Converts units (wind: m/s → km/h, visibility: m → km)
- Returns validated Pydantic model

**API Call:**
```
GET https://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_KEY&units=metric
```

**Raw API Response (nested):**
```json
{
  "name": "London",
  "sys": {"country": "GB", "sunrise": 1681561200, "sunset": 1681610400},
  "main": {
    "temp": 15.5,
    "feels_like": 14.2,
    "humidity": 72,
    "pressure": 1013
  },
  "wind": {
    "speed": 5.2,      // in m/s (need to convert to km/h)
    "deg": 230
  },
  "weather": [{"description": "partly cloudy", "main": "Clouds"}],
  "clouds": {"all": 50},
  "visibility": 10000,  // in meters (need to convert to km)
  "dt": 1681589400
}
```

**Transformation Logic:**
```python
# Wind speed: m/s to km/h (multiply by 3.6)
5.2 m/s * 3.6 = 18.72 km/h

# Visibility: meters to km (multiply by 0.001)
10000 m * 0.001 = 10.0 km
```

**Flattened Response (returned):**
```json
{
  "city": "London",
  "country": "GB",
  "temperature_celsius": 15.5,
  "feels_like_celsius": 14.2,
  "humidity_percent": 72,
  "description": "partly cloudy",
  "wind_speed_kmh": 18.72,
  "wind_direction_degrees": 230,
  "pressure_hpa": 1013,
  "visibility_km": 10.0,
  "clouds_percent": 50
}
```

### 2. `get_forecast(city: str) → ForecastResponse`

**What it does:**
- Calls OpenWeatherMap's `/data/2.5/forecast` endpoint
- Receives 40 items (5 days × 8 intervals per day)
- **Groups 3-hour intervals into daily summaries**
- Returns daily min/max temps, average conditions
- Calculates rain probability

**API Call:**
```
GET https://api.openweathermap.org/data/2.5/forecast?q=London&appid=YOUR_KEY&units=metric
```

**Raw API Response:**
```json
{
  "city": {"name": "London", "country": "GB"},
  "list": [
    {"dt": 1681603200, "main": {"temp": 14.2, ...}, "weather": [...], ...},  // 3 hours 1
    {"dt": 1681606800, "main": {"temp": 15.1, ...}, "weather": [...], ...},  // 3 hours 2
    {"dt": 1681610400, "main": {"temp": 16.5, ...}, "weather": [...], ...},  // 3 hours 3
    // ... 37 more items (40 total for 5 days)
  ]
}
```

**Daily Summary Calculation:**
```python
# For April 14, 2025, there are 8 forecast items (one every 3 hours)
# Day: April 14, 2025
items_for_day = [
    item1: temp=12.0, humidity=70, description="cloudy", wind=5.0 m/s
    item2: temp=13.5, humidity=68, description="cloudy", wind=5.5 m/s
    item3: temp=15.0, humidity=65, description="partly cloudy", wind=6.0 m/s
    item4: temp=16.5, humidity=62, description="clear", wind=6.5 m/s  (warmest)
    item5: temp=15.2, humidity=64, description="partly cloudy", wind=6.2 m/s
    item6: temp=14.0, humidity=66, description="cloudy", wind=5.8 m/s
    item7: temp=13.0, humidity=68, description="cloudy", wind=5.5 m/s
    item8: temp=12.0, humidity=70, description="cloudy", wind=5.0 m/s  (coolest)
]

# Calculate aggregates:
# Min temp: 12.0
# Max temp: 16.5
# Avg humidity: (70+68+65+62+64+66+68+70) / 8 = 66%
# Most common description: "cloudy" (appears 4 times)
# Avg wind speed: (5.0+5.5+6.0+6.5+6.2+5.8+5.5+5.0) / 8 = 5.69 m/s = 20.48 km/h
# Rain chance: 2 out of 8 items have rain = 25%
```

**Flattened Daily Response:**
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
      "wind_speed_kmh": 20.48,
      "rain_chance_percent": 25.0
    },
    {
      "date": "2025-04-15",
      "temp_min_celsius": 11.5,
      "temp_max_celsius": 17.2,
      // ...
    },
    // ... 3 more days
  ]
}
```

### 3. `get_air_quality(city: str) → AirQualityResponse`

**What it does:**
1. **Step 1: Geocode** - Convert city name to coordinates
   - Calls `/geo/1.0/direct` with city name
   - Gets latitude and longitude
   
2. **Step 2: Fetch Air Quality** - Use coordinates to get AQI
   - Calls `/data/2.5/air_pollution` with lat/lon
   - Gets AQI value and pollutant concentrations
   
3. **Transform** - Map AQI integer to human label
   - 1 → "Good"
   - 2 → "Fair"
   - 3 → "Moderate"
   - 4 → "Poor"
   - 5 → "Very Poor"

**Flow Diagram:**
```
User: "Get air quality for London"
    ↓
Step 1: Geocode "London"
    GET /geo/1.0/direct?q=London&appid=KEY&limit=1
    Returns: [{"lat": 51.5074, "lon": -0.1278, ...}]
    ↓
Step 2: Call Air Quality API with lat/lon
    GET /data/2.5/air_pollution?lat=51.5074&lon=-0.1278&appid=KEY
    ↓
Step 3: Transform and return
    AQI: 2 → "Fair"
    Components: PM2.5, PM10, CO, NO2, O3
```

**Raw Geocoding Response:**
```json
[
  {
    "name": "London",
    "lat": 51.5074,
    "lon": -0.1278,
    "country": "GB"
  }
]
```

**Raw Air Quality Response:**
```json
{
  "list": [
    {
      "main": {
        "aqi": 2  // 1=Good, 2=Fair, 3=Moderate, 4=Poor, 5=Very Poor
      },
      "components": {
        "pm2_5": 25.5,   // μg/m³
        "pm10": 45.0,
        "co": 150.0,
        "no2": 32.0,
        "o3": 65.5,
        "so2": null
      },
      "dt": 1681603200
    }
  ]
}
```

**Transformation:**
```python
aqi_value = 2
aqi_label = AQI_LABELS[2]  # "Fair"
```

**Flattened Response:**
```json
{
  "city": "London",
  "aqi": 2,
  "aqi_label": "Fair",
  "pm2_5": 25.5,
  "pm10": 45.0,
  "co": 150.0,
  "no2": 32.0,
  "o3": 65.5
}
```

## Unit Conversions

| Quantity | OpenWeatherMap | Our API | Conversion |
|----------|---|---|---|
| Wind Speed | m/s | km/h | multiply by 3.6 |
| Visibility | meters | km | multiply by 0.001 (or divide by 1000) |
| Temperature | Celsius | Celsius | no conversion (metric units) |
| Pollutants | μg/m³ | μg/m³ | no conversion |

## Error Handling

All three functions raise `ValueError` for known error cases:

| Error | When | Message |
|-------|------|---------|
| Not Found | City doesn't exist | `"City '{city}' not found"` |
| Network Error | Can't connect | `"Unable to connect to OpenWeatherMap API"` |
| API Error | 5xx response | `"OpenWeatherMap API error: {status_code}"` |
| Geocoding Error | Coordinate lookup fails | `"Unable to connect to geocoding service"` |

## Configuration

All functions use:
- **API Key**: `config.OPENWEATHER_API_KEY` (from `.env`)
- **Base URL**: `config.OPENWEATHER_BASE_URL` = `"https://api.openweathermap.org"`
- **Units**: Always "metric" (Celsius, m/s, etc.)

## Async/Await Pattern

```python
async def get_current_weather(city: str) -> CurrentWeatherResponse:
    # Creates an async HTTP client
    async with httpx.AsyncClient() as client:
        # Makes non-blocking HTTP request
        response = await client.get(url, params=params)
        # Waits for response without blocking other requests
        data = response.json()
    
    # Transform and return
    return CurrentWeatherResponse(...)
```

**Benefits:**
- Multiple requests don't block each other
- Server can handle many simultaneous requests
- No thread overhead, uses async/await

## DRY Principle

The three functions share common patterns:

| Pattern | Location |
|---------|----------|
| Error handling try/except | Each function (duplicate) |
| HTTP client creation | `async with httpx.AsyncClient()` |
| JSON parsing | `response.json()` |
| AQI label mapping | `AQI_LABELS` constant |
| Unit conversions | `MS_TO_KMH`, `METERS_TO_KM` constants |

## Testing (Example)

```python
import asyncio
from services import get_current_weather

async def test():
    result = await get_current_weather("London")
    assert result.city == "London"
    assert result.temperature_celsius > -50  # sanity check
    print("✓ Current weather works!")

asyncio.run(test())
```

## Summary Table

| Function | Endpoint | Input | Output | Units | Special |
|----------|----------|-------|--------|-------|---------|
| `get_current_weather` | `/data/2.5/weather` | city | Current conditions | Celsius, km/h, km, % | Single moment in time |
| `get_forecast` | `/data/2.5/forecast` | city | 5 daily summaries | Celsius, km/h, km, % | Groups 3-hr intervals → daily |
| `get_air_quality` | `/data/2.5/air_pollution` | city | AQI + pollutants | AQI (1-5), μg/m³ | Geocodes first |

