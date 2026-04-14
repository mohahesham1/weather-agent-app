
# --- DEBUG ENVIRONMENT INFO ---
import sys
print("[DEBUG] Python executable:", sys.executable)
print("[DEBUG] sys.path:", sys.path)
try:
    import uvicorn
    print("[DEBUG] Successfully imported uvicorn, version:", uvicorn.__version__)
except Exception as e:
    print("[DEBUG] Failed to import uvicorn:", e)
try:
    import fastapi
    print("[DEBUG] Successfully imported fastapi, version:", fastapi.__version__)
except Exception as e:
    print("[DEBUG] Failed to import fastapi:", e)
try:
    import aiohttp
    print("[DEBUG] Successfully imported aiohttp, version:", aiohttp.__version__)
except Exception as e:
    print("[DEBUG] Failed to import aiohttp:", e)
print("[DEBUG] Starting main.py...")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from agent import agent_executor

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

    try:
        result = await agent_executor.ainvoke({
            "messages": [HumanMessage(content=request.message)]
        })
        # LangGraph's create_react_agent expects messages format
        # Result will be a dict with {"messages": [...]} containing all conversation messages

        # Extract the response from the messages
        response_text = None
        
        if isinstance(result, dict) and "messages" in result:
            messages = result.get("messages", [])
            # Get the last message (should be AI response)
            if messages:
                last_msg = messages[-1]
                if hasattr(last_msg, "content"):
                    response_text = last_msg.content
                elif isinstance(last_msg, dict) and "content" in last_msg:
                    response_text = last_msg["content"]
        
        # Fallback if we can't extract from messages
        if not response_text:
            response_text = result.get("output", str(result)) if isinstance(result, dict) else str(result)
        
        return ChatResponse(response=response_text)
    
    except Exception as e:
        # If agent fails, return helpful error message
        return ChatResponse(response=f"I encountered an error processing your request: {str(e)}")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "weather-agent-backend"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=False)