
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
# The key that authenticates with Google's Gemini API.
# LangChain's ChatGoogleGenerativeAI will use this.

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
# Where our MCP Server is running.
# Default to localhost:8000 if not specified.
# The tools in tools.py will use this to make HTTP calls.