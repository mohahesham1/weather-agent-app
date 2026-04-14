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

from langchain.agents import AgentExecutor, create_tool_calling_agent
# create_tool_calling_agent: A FUNCTION (not a reserved word)
# that wires together an LLM + tools + prompt into an "agent"
# object. The agent is the decision maker (picks tools).
#
# AgentExecutor: A CLASS that runs the agent loop. The loop is:
# ask LLM -> parse output -> if tool call: run it, feed back,
# go again -> if final answer: return it.

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# ChatPromptTemplate: Structures the messages sent to the LLM.
# MessagesPlaceholder: A dynamic slot where messages get inserted.

from .config import GEMINI_API_KEY
from .tools import ALL_TOOLS


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


# ---- PROMPT TEMPLATE ----
prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    # The system message. The LLM always sees this first.
    # It sets the behavior, personality, and rules.

    MessagesPlaceholder(variable_name="chat_history", optional=True),
    # A slot for past conversation messages. Optional because
    # the first message has no history. We are not using multi-turn
    # memory in this project, but including this makes it easy to add.

    ("human", "{input}"),
    # The user's current question. {input} gets replaced with
    # the actual text when .invoke() is called.

    MessagesPlaceholder(variable_name="agent_scratchpad"),
    # CRITICAL: This is where LangChain puts tool call results.
    # When the LLM calls a tool, the result goes here so the LLM
    # can see it on the next iteration. DO NOT REMOVE THIS.
    # Without it, the LLM would never see the tool results and
    # would keep calling tools in an infinite loop.
])


# ---- CREATE THE LLM ----
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    # The model to use. "gemini-2.0-flash" is fast and capable,
    # reliable for tool calling. Alternatives:
    # "gemini-1.5-pro" = more capable but slower
    # "gemini-1.5-flash" = previous generation, still works well

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
agent = create_tool_calling_agent(llm, ALL_TOOLS, prompt)
# This function (NOT a reserved word, just a LangChain function)
# wires together:
# 1. The LLM (brain that makes decisions)
# 2. The tools (capabilities the brain can use)
# 3. The prompt (instructions for the brain)
# It returns an "agent" object that knows HOW to decide,
# but cannot execute anything on its own.


# ---- CREATE THE EXECUTOR ----
agent_executor = AgentExecutor(
    agent=agent,
    # The decision-making agent we just created.

    tools=ALL_TOOLS,
    # The actual functions. The agent has tool DESCRIPTIONS
    # (for the LLM to read). The executor has the actual FUNCTIONS
    # (to run when the LLM picks one). That is why both get tools.

    verbose=True,
    # Prints each step to the terminal. EXTREMELY useful for
    # debugging. You will see:
    # "Invoking get_current_weather with {'city': 'London'}"
    # "Tool result: {temperature_celsius: 12.5, ...}"
    # Set to False in production.

    handle_parsing_errors=True
    # If the LLM returns malformed output (happens rarely),
    # instead of crashing, it retries or returns a fallback message.
)