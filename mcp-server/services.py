# ============================================================
# services.py
# ============================================================
# PURPOSE: Make actual HTTP calls to OpenWeatherMap's API.
#
# WHY A SEPARATE FILE FROM main.py?
# main.py handles WEB REQUESTS (FastAPI routes).
# services.py handles API CALLS (external HTTP requests).
# This separation means:
#   - If OpenWeatherMap changes their API, only this file changes.
#   - If we add a new web route, services.py is untouched.
#   - Each file has one responsibility (Single Responsibility Principle).
# ============================================================

import httpx
# httpx is an HTTP client library, similar to "requests" but with
# one critical difference: httpx supports ASYNC requests.
#
# WHY NOT USE "requests"?
# "requests" is synchronous. When it makes an HTTP call, it BLOCKS
# the entire server until the response comes back. If 10 users
# hit your API at once, user #10 waits for all 9 before them.
# httpx with "async/await" lets the server handle other requests
# WHILE waiting for OpenWeatherMap to respond. Much faster.

from .config import OPENWEATHER_API_KEY, OPENWEATHER_BASE_URL
# The dot (.) in ".config" means "import from the config.py file
# in the SAME package (same folder)." This is called a relative import.
# Without the dot, Python would look for a global package called "config."

# A dictionary that maps AQI numbers to human-readable labels.
# OpenWeatherMap returns 1-5, but "Good" is more useful than "1".
AQI_LABELS = {
    1: "Good",
    2: "Fair",
    3: "Moderate",
    4: "Poor",
    5: "Very Poor"
}


async def get_current_weather(city: str) -> dict:
    # "async def" marks this as an ASYNCHRONOUS function.
    # That means it can "pause" (await) while waiting for HTTP
    # responses without blocking other code from running.
    #
    # "city: str" means the parameter "city" must be a string.
    # "-> dict" means this function returns a dictionary.

    """Fetch current weather for a city from OpenWeatherMap."""

    async with httpx.AsyncClient() as client:
        # "async with" creates an HTTP client and GUARANTEES it
        # gets properly closed when we are done, even if an error
        # occurs. This prevents connection leaks.
        #
        # Think of it like opening a file: you always want to close
        # it when done. "async with" does that automatically.

        response = await client.get(
            # client.get() makes an HTTP GET request.
            # "await" pauses this function until the response arrives.
            # While paused, the server can handle other requests.

            f"{OPENWEATHER_BASE_URL}/data/2.5/weather",
            # f"..." is an f-string. The {OPENWEATHER_BASE_URL} part
            # gets replaced with the actual URL value.
            # Result: "https://api.openweathermap.org/data/2.5/weather"

            params={
                "q": city,                        # q = query. The city name.
                "appid": OPENWEATHER_API_KEY,     # Authentication key.
                "units": "metric"                # Return Celsius not Kelvin.
            }
            # params={} adds query parameters to the URL.
            # The actual request becomes:
            # GET /data/2.5/weather?q=London&appid=xxx&units=metric
        )

        response.raise_for_status()
        # If the response status code is 4xx or 5xx (an error),
        # this throws an exception immediately. Without this,
        # we would silently try to parse an error response as
        # weather data, which would crash in confusing ways.
        # Common errors: 404 = city not found, 401 = bad API key.

        data = response.json()
        # .json() parses the response body from JSON text into
        # a Python dictionary. OpenWeatherMap returns something like:
        # {"main": {"temp": 18.5, "humidity": 72, ...}, "wind": {"speed": 4.2, ...}, ...}
        # This is deeply nested. We flatten it below.

    return {
        "city": data["name"],
        # data["name"] extracts the city name from the response.
        # We use the API's version because it is properly capitalized.

        "country": data["sys"]["country"],
        # Nested access: data -> "sys" object -> "country" field.
        # Returns "GB", "US", "EG" etc.

        "temperature_celsius": data["main"]["temp"],
        # The raw API nests temperature inside data["main"]["temp"].
        # We flatten it to just "temperature_celsius" for clarity.

        "feels_like_celsius": data["main"]["feels_like"],
        # "Feels like" accounts for wind chill and humidity.

        "humidity_percent": data["main"]["humidity"],

        "description": data["weather"][0]["description"],
        # data["weather"] is a LIST (array). [0] gets the first item.
        # There can be multiple weather conditions (rare), we take the primary one.

        "wind_speed_kmh": round(data["wind"]["speed"] * 3.6, 1),
        # OpenWeatherMap returns wind in METERS PER SECOND.
        # To convert m/s to km/h: multiply by 3.6
        # (because 1 km = 1000m and 1 hour = 3600 seconds)
        # round(..., 1) rounds to 1 decimal place: 15.28 becomes 15.3

        "wind_direction_degrees": data["wind"].get("deg", 0),
        # .get("deg", 0) is SAFE dictionary access.
        # If "deg" exists, return its value.
        # If "deg" is MISSING, return 0 instead of crashing.
        # Some API responses omit wind direction.

        "pressure_hpa": data["main"]["pressure"],

        "visibility_km": round(data.get("visibility", 10000) / 1000, 1),
        # Visibility comes in METERS. We divide by 1000 to get KM.
        # Default 10000 (10km) if the field is missing.

        "clouds_percent": data["clouds"]["all"]
        # 0 = clear sky, 100 = completely overcast
    }


async def get_forecast(city: str) -> dict:
    """Fetch 5-day forecast, aggregated from 3-hour intervals to daily."""

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{OPENWEATHER_BASE_URL}/data/2.5/forecast",
            params={"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric"}
        )
        response.raise_for_status()
        data = response.json()

    # OpenWeatherMap returns 40 entries (8 per day x 5 days).
    # Each entry is a 3-hour window (00:00, 03:00, 06:00, ...).
    # We group them by date to get daily summaries.

    daily = {}  # Will hold date -> list of values

    for entry in data["list"]:
        # data["list"] is the array of 40 forecast entries.
        # Each entry has: dt_txt, main, weather, wind, pop, etc.

        date = entry["dt_txt"].split(" ")[0]
        # dt_txt looks like "2025-04-15 12:00:00"
        # .split(" ") splits it into ["2025-04-15", "12:00:00"]
        # [0] takes the first part: "2025-04-15"

        if date not in daily:
            daily[date] = {
                "temps": [], "humidity": [], "wind": [],
                "descriptions": [], "rain_probs": []
            }
            # First time seeing this date, create empty lists.

        # Append this entry's data to the day's lists
        daily[date]["temps"].append(entry["main"]["temp"])
        daily[date]["humidity"].append(entry["main"]["humidity"])
        daily[date]["wind"].append(entry["wind"]["speed"])
        daily[date]["descriptions"].append(entry["weather"][0]["description"])
        daily[date]["rain_probs"].append(entry.get("pop", 0))
        # "pop" = Probability Of Precipitation, a float from 0 to 1.
        # 0.8 means 80% chance of rain. Defaults to 0 if missing.

    # Build clean daily summaries from the grouped data
    forecast_days = []
    for date, values in list(daily.items())[:5]:
        # daily.items() gives (date, values) pairs.
        # [:5] limits to 5 days maximum.

        forecast_days.append({
            "date": date,
            "temp_min_celsius": round(min(values["temps"]), 1),
            # min() finds the lowest temperature of the day.

            "temp_max_celsius": round(max(values["temps"]), 1),
            # max() finds the highest temperature of the day.

            "humidity_percent": round(
                sum(values["humidity"]) / len(values["humidity"])
            ),
            # Average humidity: sum all values, divide by count.

            "description": max(
                set(values["descriptions"]),
                key=values["descriptions"].count
            ),
            # Find the MOST COMMON description for the day.
            # set() gets unique values. max(..., key=.count) finds
            # which one appears most often. This is called "mode."

            "wind_speed_kmh": round(max(values["wind"]) * 3.6, 1),
            # Peak wind speed of the day, converted to km/h.

            "rain_chance_percent": round(max(values["rain_probs"]) * 100, 1)
            # Highest rain probability of the day, converted to %.
            # max([0.2, 0.8, 0.3]) = 0.8, * 100 = 80.0%
        })

    return {
        "city": data["city"]["name"],
        "country": data["city"]["country"],
        "forecast": forecast_days
    }


async def get_air_quality(city: str) -> dict:
    """Fetch air quality data. Requires two API calls (geocode then AQI)."""

    async with httpx.AsyncClient() as client:
        # STEP 1: Convert city name to lat/lon coordinates.
        # The air quality API does NOT accept city names,
        # only coordinates. So we must geocode first.
        geo_response = await client.get(
            f"{OPENWEATHER_BASE_URL}/geo/1.0/direct",
            params={"q": city, "limit": 1, "appid": OPENWEATHER_API_KEY}
            # "limit": 1 means "return only the top match"
        )
        geo_response.raise_for_status()
        geo_data = geo_response.json()

        if not geo_data:
            # If the list is empty, the city was not found.
            raise ValueError(f"City '{city}' not found")

        lat = geo_data[0]["lat"]   # First result's latitude
        lon = geo_data[0]["lon"]   # First result's longitude

        # STEP 2: Get air quality using the coordinates.
        aq_response = await client.get(
            f"{OPENWEATHER_BASE_URL}/data/2.5/air_pollution",
            params={"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY}
        )
        aq_response.raise_for_status()
        aq_data = aq_response.json()

    aqi = aq_data["list"][0]["main"]["aqi"]
    components = aq_data["list"][0]["components"]

    return {
        "city": city,
        "aqi": aqi,
        "aqi_label": AQI_LABELS.get(aqi, "Unknown"),
        # .get(aqi, "Unknown") safely looks up the label.
        # If aqi is somehow not 1-5, returns "Unknown".
        "pm2_5": components.get("pm2_5"),
        "pm10": components.get("pm10"),
        "co": components.get("co"),
        "no2": components.get("no2"),
        "o3": components.get("o3")
    }