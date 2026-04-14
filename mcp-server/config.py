# ============================================================
# config.py
# ============================================================
# PURPOSE: Load secret API keys from the .env file.
#
# WHY A SEPARATE CONFIG FILE?
# If every file loaded its own environment variables, you
# would have dotenv logic scattered everywhere. By centralizing
# it in config.py, there is ONE place to manage all config.
# Other files just import from config. Clean and DRY (Don't
# Repeat Yourself).
# ============================================================

import os
# os is a BUILT-IN Python module (no pip install needed).
# os.getenv() reads environment variables from the system.
# os.path.join() builds file paths that work on any OS
# (uses / on Mac/Linux, \ on Windows automatically).

from dotenv import load_dotenv
# load_dotenv is from the "python-dotenv" pip package.
# It reads a .env file and sets each line as an environment
# variable. Without this, you would have to manually export
# every variable in your terminal before running the server.

# Build the path to the .env file.
# __file__ = the current file (config.py)
# os.path.dirname(__file__) = the folder config.py is in (mcp-server/)
# ".." = go up one level (to the project root)
# ".env" = the file name
# Result: something like /home/user/weather-agent-app/.env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

# Read the API key from environment variables.
# os.getenv("NAME", "default") returns:
#   - The value of the variable if it exists
#   - The default ("") if it does not exist
# The empty string default prevents None errors downstream.
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

# Base URL for OpenWeatherMap API.
# Stored as a constant (ALL_CAPS by Python convention) so if
# the URL ever changes, we update it in one place only.
OPENWEATHER_BASE_URL = "https://api.openweathermap.org"