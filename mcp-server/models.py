# ============================================================
# models.py
# ============================================================
# PURPOSE: Define the exact shape of data our API returns.
#
# WHAT IS PYDANTIC?
# Pydantic is a data validation library. You define a class
# with typed fields, and Pydantic ensures any data you put
# into it matches those types. If you try to put a string
# where an int should be, it throws a clear error.
#
# WHY NOT JUST USE DICTIONARIES?
# Dicts have no validation. You could accidentally return
# {"tmperature": 20} (typo) and nobody catches it until
# the frontend breaks. With Pydantic, the schema is enforced.
# FastAPI also uses these models to auto-generate API docs.
# ============================================================

from pydantic import BaseModel
# BaseModel is the parent class. Every model we define
# inherits from it, which gives it validation superpowers.

from typing import Optional, List
# typing is a BUILT-IN Python module for type annotations.
# Optional[float] means "this field can be a float OR None"
# List[ForecastDay] means "a list where every item is a ForecastDay"


class CurrentWeatherResponse(BaseModel):
    # This class defines what a "current weather" API response
    # looks like. Every field has a name and a type.
    # When FastAPI returns this, it automatically converts it to JSON.

    city: str                          # "London", "Cairo" etc.
    country: str                       # "GB", "EG" (ISO country code)
    temperature_celsius: float        # 18.5 (decimal number)
    feels_like_celsius: float         # What it "feels like" with wind chill
    humidity_percent: int             # 0-100 integer
    description: str                   # "scattered clouds", "clear sky"
    wind_speed_kmh: float             # Wind in km/h (we convert from m/s)
    wind_direction_degrees: int       # 0=North, 90=East, 180=South, 270=West
    pressure_hpa: int                 # Atmospheric pressure in hectopascals
    visibility_km: float              # How far you can see in km
    clouds_percent: int               # 0=clear sky, 100=fully overcast


class ForecastDay(BaseModel):
    # One day within a 5-day forecast.
    # The ForecastResponse below contains a List of these.

    date: str                           # "2025-04-15"
    temp_min_celsius: float             # Lowest temp that day
    temp_max_celsius: float             # Highest temp that day
    humidity_percent: int
    description: str                    # Most common condition that day
    wind_speed_kmh: float
    rain_chance_percent: Optional[float] = None
    # Optional means this field CAN be None (missing).
    # = None sets the default value to None if not provided.
    # Some days have no rain data, so we make it optional.


class ForecastResponse(BaseModel):
    city: str
    country: str
    forecast: List[ForecastDay]
    # List[ForecastDay] means: an array where each element
    # must be a valid ForecastDay object. Pydantic validates
    # every item in the list automatically.


class AirQualityResponse(BaseModel):
    city: str
    aqi: int                            # 1=Good, 2=Fair, 3=Moderate, 4=Poor, 5=Very Poor
    aqi_label: str                      # Human-readable: "Good", "Fair", etc.
    pm2_5: Optional[float] = None     # Fine particles (dangerous to lungs)
    pm10: Optional[float] = None      # Coarser particles
    co: Optional[float] = None        # Carbon monoxide
    no2: Optional[float] = None       # Nitrogen dioxide
    o3: Optional[float] = None        # Ozone