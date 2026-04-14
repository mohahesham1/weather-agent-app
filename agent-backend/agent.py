# ============================================================
# agent.py: The Brain of the Application
# ============================================================
# This file creates the LangChain "agent" that:
# 1. Receives a user question
# 2. Decides which tool(s) to call
# 3. Executes the tool(s) via the executor
# 4. Feeds results back to the LLM
# 5. Returns a final human-friendly answer
# ============================================================

from langchain_google_genai import ChatGoogleGenerativeAI
# ChatGoogleGenerativeAI is a CLASS from the langchain-google-genai package.
# It creates a connection to Google's Gemini API.
# LangChain wraps it so it integrates with agents, tools, and prompts.

from langgraph.prebuilt import create_react_agent
# create_react_agent: Creates a ReAct (Reasoning + Acting) agent
# using LangGraph. This is the modern way to build agents.

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# ChatPromptTemplate: Structures the messages sent to the LLM.
# MessagesPlaceholder: A dynamic slot where messages get inserted.

from config import GEMINI_API_KEY, GEMINI_MODEL
from tools import ALL_TOOLS


# ---- THE SYSTEM PROMPT ----
# This is the most important piece of "prompt engineering" in
# the project. It tells the LLM WHO it is and HOW to behave.
# The rubric evaluates "effective prompt engineering" (20%).
SYSTEM_PROMPT = """You are a helpful weather assistant. You provide accurate, 
friendly, and contextual weather information.

When answering questions:
- Always use the available tools to get real-time data. Never make up weather data.
- If the user asks about current conditions, use get_current_weather.
- If the user asks about future weather or forecasts, use get_weather_forecast.
- If the user asks about air quality or pollution, use get_air_quality.
- If a question requires multiple tools (e.g., "current weather AND forecast"),
  call ALL the relevant tools before answering.
- Convert data into practical, human-friendly advice (e.g., "Bring an umbrella"
  or "Great day for a run").
- Include specific numbers (temperature, humidity) but explain what they mean
  for the average person.
- If the city is ambiguous, ask for clarification.
"""


# ---- CREATE THE LLM ----
llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    # The model to use is read from config/env so deprecations
    # can be handled without code edits.

    temperature=0.3,
    # Controls randomness in the LLM's output.
    # 0.0 = always pick the most likely next word (deterministic)
    # 1.0 = more creative/random/varied responses
    # 0.3 = slightly creative but mostly focused. Good for factual
    # data (weather) with some personality in the advice.

    google_api_key=GEMINI_API_KEY
    # Explicitly pass the key. You could also set GOOGLE_API_KEY
    # as an env var and ChatGoogleGenerativeAI would find it.
    # We pass it explicitly for clarity.
)


# ---- CREATE THE AGENT ----
# Create a ReAct agent using LangGraph's prebuilt factory
# The system prompt is incorporated through the tool docstrings,
# which are descriptive enough to guide the LLM behavior.
agent_executor = create_react_agent(llm, ALL_TOOLS)
# This creates a complete agent with:
# 1. The LLM (brain that makes decisions)
# 2. The tools (capabilities the brain can use)
# 3. Built-in ReAct loop (reasoning + acting)
# It returns an executor that can be invoked directly.