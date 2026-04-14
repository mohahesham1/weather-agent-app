from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .agent import agent_executor

app = FastAPI(
    title="Weather Agent Backend",
    description="LLM-powered weather assistant",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    # The frontend sends: {"message": "What's the weather in Cairo?"}
    # Pydantic validates that "message" exists and is a string.
    # If the frontend sends {} (no message), FastAPI returns 422 error.

class ChatResponse(BaseModel):
    response: str
    # We return: {"response": "It's currently 35C in Cairo..."}


@app.post("/chat", response_model=ChatResponse)
# POST (not GET) because we are SENDING data (the user's message).
# GET is for RETRIEVING data. POST is for SENDING data.
# This is a REST API convention.

async def chat(request: ChatRequest):
    # FastAPI automatically:
    # 1. Reads the JSON body from the HTTP request
    # 2. Validates it against ChatRequest
    # 3. Passes it as the "request" parameter

    """Process a user message through the LangChain agent."""

    result = await agent_executor.ainvoke({
        "input": request.message
    })
    # .ainvoke() is the ASYNC version of .invoke().
    # It starts the full agent loop:
    # user question -> LLM -> tool calls -> results -> final answer
    #
    # {"input": request.message} passes the user's text to the
    # {input} placeholder in the prompt template.
    #
    # The result is a dict like:
    # {"input": "What's the weather?", "output": "It's 35C in..."}

    return ChatResponse(response=result["output"])
    # Extract just the "output" (the agent's final answer)
    # and wrap it in a ChatResponse for validation.


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "weather-agent-backend"}