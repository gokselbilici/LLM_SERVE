from fastapi import FastAPI, Request, Body
from fastapi.responses import JSONResponse
import httpx
from pydantic import BaseModel
from typing import List, Literal, Optional
import constants as c
import logging
import os

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/controller.log", mode="a", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("local_llm_api_controller")

# Pydantic models for request
class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class ChatCompletionRequest(BaseModel):
    messages: List[Message]
    temperature: float = 0.7
    top_p: float = 0.8
    max_tokens: int = 512

class ModelPermission(BaseModel):
    id: str
    object: str
    created: int
    allow_create_engine: bool
    allow_sampling: bool
    allow_logprobs: bool
    allow_search_indices: bool
    allow_view: bool
    allow_fine_tuning: bool
    organization: str
    group: Optional[str]
    is_blocking: bool

class ModelData(BaseModel):
    id: str
    object: str
    created: int
    owned_by: str
    root: str
    parent: Optional[str]
    max_model_len: int
    permission: List[ModelPermission]

class ModelsResponse(BaseModel):
    object: str
    data: List[ModelData]

app = FastAPI()

@app.get("/v1/models", response_model=ModelsResponse)
async def get_models():
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{c.LLM_BACKEND_URL}/v1/models")
            response.raise_for_status()
            logger.info("Fetched model list from vLLM engine.")
            return response.json()  # FastAPI will validate and serialize this to `ModelsResponse`
    except httpx.HTTPError as e:
        logger.error("HTTP error from llm_engine on /v1/models: %s", str(e))
        return JSONResponse(status_code=502, content={"error": "Failed to connect to backend."})
    except Exception as e:
        logger.exception("Unexpected error in /v1/models")
        return JSONResponse(status_code=500, content={"error": "Internal server error"})


@app.post("/v1/chat/completions")
async def chat_completions(payload: ChatCompletionRequest = Body(...)):
    payload_dict = payload.dict()
    logger.info("Received /v1/chat/completions request with %d messages", len(payload_dict["messages"]))

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(f"{c.LLM_BACKEND_URL}/v1/chat/completions", json=payload_dict)
            response.raise_for_status()

            # Log response summary
            json_response = response.json()
            logger.info("LLM backend responded successfully.")
            logger.debug("LLM response: %s", str(json_response)[:500])  # log only first 500 chars

            return JSONResponse(content=json_response)

    except httpx.HTTPError as e:
        logger.error("HTTP error from llm_engine: %s", str(e))
        return JSONResponse(status_code=502, content={"error": "Failed to connect to backend."})

    except Exception as e:
        logger.exception("Unexpected error during request.")
        return JSONResponse(status_code=500, content={"error": "Internal server error"})

@app.get("/")
def root():
    logger.info("Health check hit: /")
    return {"status": "✅ Controller is up and running!"}