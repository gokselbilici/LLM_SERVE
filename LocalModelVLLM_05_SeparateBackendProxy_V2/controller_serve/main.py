from fastapi import FastAPI, Request, Body, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
from pydantic import BaseModel, Field, validator
from typing import List, Literal, Optional, Dict, Any
import constants as c
import logging
import os
import time
import asyncio
from contextlib import asynccontextmanager
from collections import defaultdict
from datetime import datetime, timedelta

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Configure logging
logging.basicConfig(
    level=getattr(logging, c.LOG_LEVEL),
    format=c.LOG_FORMAT,
    handlers=[
        logging.FileHandler("logs/controller.log", mode="a", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("local_llm_api_controller")

# Global variables for health checking and rate limiting
backend_healthy = True
last_health_check = 0
rate_limit_store = defaultdict(list)

# Enhanced Pydantic models
class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(..., min_length=1, max_length=10000)

class ChatCompletionRequest(BaseModel):
    messages: List[Message] = Field(..., min_items=1, max_items=100)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=0.8, ge=0.0, le=1.0)
    max_tokens: int = Field(default=512, ge=1, le=4096)
    stream: bool = Field(default=False)
    
    @validator('messages')
    def validate_messages(cls, v):
        if not v:
            raise ValueError("Messages cannot be empty")
        return v

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
    group: Optional[str] = None
    is_blocking: bool

class ModelData(BaseModel):
    id: str
    object: str
    created: int
    owned_by: str
    root: str
    parent: Optional[str] = None
    max_model_len: int
    permission: List[ModelPermission]

class ModelsResponse(BaseModel):
    object: str
    data: List[ModelData]

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    backend_healthy: bool
    version: str

class ErrorResponse(BaseModel):
    error: str
    timestamp: str
    request_id: Optional[str] = None

# Rate limiting dependency
async def rate_limit_check(request: Request):
    client_ip = request.client.host
    current_time = datetime.now()
    
    # Clean old requests
    rate_limit_store[client_ip] = [
        req_time for req_time in rate_limit_store[client_ip]
        if current_time - req_time < timedelta(minutes=1)
    ]
    
    # Check rate limit
    if len(rate_limit_store[client_ip]) >= c.RATE_LIMIT_PER_MINUTE:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )
    
    # Record current request
    rate_limit_store[client_ip].append(current_time)

# Health check for backend
async def check_backend_health():
    global backend_healthy, last_health_check
    current_time = time.time()
    
    # Check every 30 seconds
    if current_time - last_health_check < 30:
        return backend_healthy
    
    try:
        async with httpx.AsyncClient(timeout=c.HEALTH_CHECK_TIMEOUT) as client:
            response = await client.get(f"{c.LLM_BACKEND_URL}/v1/models")
            backend_healthy = response.status_code == 200
            last_health_check = current_time
            logger.info(f"Backend health check: {'healthy' if backend_healthy else 'unhealthy'}")
            return backend_healthy
    except Exception as e:
        logger.warning(f"Backend health check failed: {str(e)}")
        backend_healthy = False
        last_health_check = current_time
        return False

# Lifespan manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {c.SERVICE_NAME} controller...")
    # Startup: Check backend health
    await check_backend_health()
    yield
    # Shutdown
    logger.info(f"Shutting down {c.SERVICE_NAME} controller...")

# FastAPI app with enhanced configuration
app = FastAPI(
    title="LLM Controller API",
    description="Proxy controller for vLLM serving with enhanced features",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enhanced error handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            timestamp=datetime.now().isoformat(),
            request_id=request.headers.get("X-Request-ID")
        ).dict()
    )

@app.get("/", response_model=HealthResponse)
async def root():
    logger.info("Health check hit: /")
    return HealthResponse(
        status="✅ Controller is up and running!",
        timestamp=datetime.now().isoformat(),
        backend_healthy=await check_backend_health(),
        version="1.0.0"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    is_healthy = await check_backend_health()
    return HealthResponse(
        status="healthy" if is_healthy else "degraded",
        timestamp=datetime.now().isoformat(),
        backend_healthy=is_healthy,
        version="1.0.0"
    )

@app.get("/v1/models", response_model=ModelsResponse)
async def get_models(request: Request, _: None = Depends(rate_limit_check)):
    request_id = request.headers.get("X-Request-ID", "unknown")
    
    try:
        async with httpx.AsyncClient(timeout=c.HEALTH_CHECK_TIMEOUT) as client:
            response = await client.get(f"{c.LLM_BACKEND_URL}/v1/models")
            response.raise_for_status()
            
            logger.info(f"Fetched model list from vLLM engine. Request ID: {request_id}")
            return response.json()
            
    except httpx.TimeoutException:
        logger.error(f"Timeout error from llm_engine on /v1/models. Request ID: {request_id}")
        raise HTTPException(status_code=504, detail="Backend timeout")
    except httpx.HTTPError as e:
        logger.error(f"HTTP error from llm_engine on /v1/models: {str(e)}. Request ID: {request_id}")
        raise HTTPException(status_code=502, detail="Failed to connect to backend")
    except Exception as e:
        logger.exception(f"Unexpected error in /v1/models. Request ID: {request_id}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/v1/chat/completions")
async def chat_completions(
    request: Request,
    payload: ChatCompletionRequest = Body(...),
    _: None = Depends(rate_limit_check)
):
    request_id = request.headers.get("X-Request-ID", f"req_{int(time.time())}")
    payload_dict = payload.dict()
    
    logger.info(f"Received /v1/chat/completions request with {len(payload_dict['messages'])} messages. Request ID: {request_id}")
    
    # Check backend health before processing
    if not await check_backend_health():
        logger.warning(f"Backend is unhealthy, rejecting request. Request ID: {request_id}")
        raise HTTPException(status_code=503, detail="Backend service unavailable")
    
    try:
        async with httpx.AsyncClient(timeout=c.BACKEND_TIMEOUT) as client:
            response = await client.post(
                f"{c.LLM_BACKEND_URL}/v1/chat/completions",
                json=payload_dict,
                headers={"X-Request-ID": request_id}
            )
            response.raise_for_status()
            
            json_response = response.json()
            
            # Log response summary
            usage = json_response.get('usage', {})
            logger.info(
                f"LLM backend responded successfully. "
                f"Tokens: {usage.get('total_tokens', 'N/A')}. "
                f"Request ID: {request_id}"
            )
            
            return JSONResponse(content=json_response)
            
    except httpx.TimeoutException:
        logger.error(f"Timeout error from llm_engine. Request ID: {request_id}")
        raise HTTPException(status_code=504, detail="Backend timeout")
    except httpx.HTTPError as e:
        logger.error(f"HTTP error from llm_engine: {str(e)}. Request ID: {request_id}")
        raise HTTPException(status_code=502, detail="Failed to connect to backend")
    except Exception as e:
        logger.exception(f"Unexpected error during request. Request ID: {request_id}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/metrics")
async def metrics():
    """Basic metrics endpoint for monitoring"""
    return {
        "backend_healthy": backend_healthy,
        "last_health_check": last_health_check,
        "active_rate_limits": len(rate_limit_store),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=c.CONTROLLER_HOST, port=c.CONTROLLER_PORT)