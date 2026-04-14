# ============================================================
# main.py: The MCP Server entry point
# ============================================================
# This file defines the HTTP ROUTES (endpoints) that clients
# can call. It does NOT contain business logic. It delegates
# all work to services.py. This keeps routes thin and clean.
# ============================================================

from fastapi import FastAPI, HTTPException, Query
# FastAPI: The class that creates the web application.
# HTTPException: A special exception that returns an HTTP error
#   response (like 400 Bad Request) instead of crashing.
# Query: Declares a query parameter with validation and docs.

from fastapi.middleware.cors import CORSMiddleware
# CORS = Cross-Origin Resource Sharing.
# Browsers block requests between different domains/ports by default.
# Our frontend (port 5173) needs to call this server (port 8000).
# CORSMiddleware tells the browser: "allow these cross-origin requests."

from .services import get_current_weather, get_forecast, get_air_quality
from .models import CurrentWeatherResponse, ForecastResponse, AirQualityResponse


app = FastAPI(
    title="Weather MCP Server",
    description="Microservice wrapper around OpenWeatherMap API",
    version="1.0.0"
)
# These parameters populate the auto-generated Swagger docs at /docs.

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Allow ALL origins (any domain/port)
    allow_credentials=True,   # Allow cookies (not needed but harmless)
    allow_methods=["*"],       # Allow GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],       # Allow any HTTP headers
)


@app.get("/health")
async def health_check():
    """Verify the server is running. Used by monitoring tools."""
    return {"status": "healthy", "service": "weather-mcp-server"}


@app.get("/weather/current", response_model=CurrentWeatherResponse)
# @app.get() is a DECORATOR that registers this function as
# the handler for GET requests to /weather/current.
#
# response_model=CurrentWeatherResponse tells FastAPI:
# "The response from this endpoint MUST match this Pydantic model."
# FastAPI will validate the response and show the schema in /docs.

async def current_weather(
    city: str = Query(..., description="City name, e.g. 'London' or 'Cairo,EG'")
    # Query(...) declares "city" as a REQUIRED query parameter.
    # The ... (Ellipsis) means "required, no default value."
    # If someone calls /weather/current without ?city=X, FastAPI
    # automatically returns a 422 error with a clear message.
    # The description= appears in the Swagger docs.
):
    """Get current weather conditions for a city."""
    try:
        return await get_current_weather(city)
        # Delegate to services.py. "await" because it is async.
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        # If anything goes wrong (city not found, API down, etc.),
        # return a 400 Bad Request with the error message.
        # Without this, the server would return a 500 Internal Error
        # with no useful information.


@app.get("/weather/forecast", response_model=ForecastResponse)
async def forecast(
    city: str = Query(..., description="City name")
):
    """Get 5-day weather forecast for a city."""
    try:
        return await get_forecast(city)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/weather/air-quality", response_model=AirQualityResponse)
async def air_quality(
    city: str = Query(..., description="City name")
):
    """Get air quality index and pollutant levels for a city."""
    try:
        return await get_air_quality(city)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))