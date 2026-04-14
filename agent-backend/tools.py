
# ============================================================
# tools.py: The Bridge Between LLM and MCP Server
# ============================================================
# WHAT IS A "TOOL" IN LANGCHAIN?
# A tool is a Python function that the LLM can DECIDE to call.
# You describe the function using a docstring, and the LLM
# reads that description to decide WHEN to use it.
#
# THE KEY INSIGHT:
# The LLM does not EXECUTE Python code. It only SAYS which
# function to call and with what arguments. LangChain catches
# that instruction and actually runs the function.
# ============================================================

import httpx
# httpx for making HTTP requests to our MCP Server.
# We use the SYNCHRONOUS version here (not async) because
# LangChain's tool executor calls these synchronously.

import json
# json.dumps() converts a Python dict to a JSON string.
# We return strings because the LLM needs text, not Python objects.

from langchain.tools import tool
# The @tool decorator converts a regular function into a
# LangChain Tool object. The decorator reads three things:
#   1. Function name -> becomes the tool name
#   2. Parameter types -> tells LLM what arguments to pass
#   3. Docstring -> tells LLM when/why to use this tool

from config import MCP_SERVER_URL


@tool
def get_current_weather(city: str) -> str:
    # city: str -> The LLM will pass a city name string.
    # -> str -> This function returns a string (JSON text).

    """Get the current weather conditions for a specific city.

    Use this tool when the user asks about current or right-now weather,
    temperature, humidity, wind speed, or general weather conditions
    for a city. Examples of questions that should trigger this tool:
    - "What's the weather in London?"
    - "Is it cold in Tokyo right now?"
    - "How humid is Cairo?"
    - "What's the temperature in New York?"

    Args:
        city: The name of the city (e.g., "London", "Cairo,EG", "New York")

    Returns:
        JSON string with temperature, humidity, wind, description, etc.
    """
    # THE DOCSTRING ABOVE IS NOT JUST DOCUMENTATION.
    # The LLM literally reads every word of it to decide when
    # to call this tool. Writing "Get weather" would be vague.
    # Writing specific examples ("Is it cold?", "How humid?")
    # helps the LLM match more user questions to this tool.
    # This IS prompt engineering, just for tools instead of chat.

    response = httpx.get(
        f"{MCP_SERVER_URL}/weather/current",
        params={"city": city}
    )
    # We call OUR MCP Server, NOT OpenWeatherMap directly.
    # Why? Because:
    # 1. The MCP Server handles the API key (we never expose it here)
    # 2. The MCP Server cleans the data (flat, consistent format)
    # 3. If we swap weather providers, this file does not change

    response.raise_for_status()
    return json.dumps(response.json(), indent=2)
    # json.dumps() converts the dict to a formatted string.
    # indent=2 makes it pretty-printed so the LLM can read it easily.
    # The LLM will receive something like:
    # {"city": "London", "temperature_celsius": 12.5, ...}


@tool
def get_weather_forecast(city: str) -> str:
    """Get the 5-day weather forecast for a specific city.

    Use this tool when the user asks about FUTURE weather, upcoming
    conditions, weekly forecast, or whether they should prepare for
    rain, cold, or heat in the coming days. Examples:
    - "What's the forecast for Paris?"
    - "Will it rain in Berlin this week?"
    - "Should I bring an umbrella to Austin tomorrow?"
    - "What will the weather be like next few days in Miami?"

    Args:
        city: The name of the city

    Returns:
        JSON string with daily forecasts including min/max temperature,
        humidity, rain chance, and weather description for 5 days.
    """
    response = httpx.get(
        f"{MCP_SERVER_URL}/weather/forecast",
        params={"city": city}
    )
    response.raise_for_status()
    return json.dumps(response.json(), indent=2)


@tool
def get_air_quality(city: str) -> str:
    """Get air quality information for a specific city.

    Use this tool when the user asks about air quality, pollution,
    AQI, smog, or whether it is safe to exercise or be outdoors.
    Examples:
    - "What's the air quality in Beijing?"
    - "Is it safe to jog outside in Delhi?"
    - "How polluted is LA right now?"
    - "Should I wear a mask in Cairo today?"

    Args:
        city: The name of the city

    Returns:
        JSON string with AQI index (1-5), human-readable label,
        and pollutant levels (PM2.5, PM10, CO, NO2, O3).
    """
    response = httpx.get(
        f"{MCP_SERVER_URL}/weather/air-quality",
        params={"city": city}
    )
    response.raise_for_status()
    return json.dumps(response.json(), indent=2)


# Export all tools as a list.
# The agent.py file imports this list and passes it to LangChain.
ALL_TOOLS = [get_current_weather, get_weather_forecast, get_air_quality]