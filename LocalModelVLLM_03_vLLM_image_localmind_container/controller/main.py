from fastapi import FastAPI, Request, Body
from fastapi.responses import StreamingResponse, JSONResponse
import httpx
from pydantic import BaseModel
from typing import List, Literal
import constants as c
from loguru import logger
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for request
class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class ChatCompletionRequest(BaseModel):
    messages: List[Message]
    temperature: float = 0.7
    top_p: float = 0.8
    max_tokens: int = 512

app = FastAPI()

@app.post("/v1/chat/completions")
async def chat_completions(payload: ChatCompletionRequest = Body(...)):
    payload_dict = payload.dict()
    logger.info("Request payload received: {}", payload_dict)

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(f"{c.LLM_BACKEND_URL}/v1/chat/completions", json=payload_dict)
            response.raise_for_status()
            logger.info("Response received from vLLM engine.")
            logger.debug("Response content: {}", response.text)
            return JSONResponse(content=response.json())

    except httpx.HTTPError as e:
        logger.error("HTTP Error from llm_engine: {}", str(e))
        return JSONResponse(status_code=502, content={"error": "Failed to connect to backend."})
    except Exception as e:
        logger.exception("Unexpected error: {}", str(e))
        return JSONResponse(status_code=500, content={"error": "Internal server error"})

@app.get("/")
def root():
    return {"status": "✅ Controller is up and running!"}