import os
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
from vllm import LLM, SamplingParams
import logging

import constants as c  # Import constants for model name and local directory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for API
class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 512
    top_p: Optional[float] = 0.9

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]

# Initialize FastAPI app
app = FastAPI(title=c.MODEL_NAME +" vLLM Server", version="1.0.0")

# Global variables
llm = None
model_name = c.MODEL_NAME  # Use the model name from constants

def initialize_model():
    """Initialize the vLLM model"""
    global llm
    
    model_path = os.environ.get('MODEL_PATH', '/app/models')
    model_subdir = f"models--{model_name.replace('/', '--')}"
    local_model_path = os.path.join(model_path, model_subdir)
    
    logger.info(f"Looking for model at: {local_model_path}")
    
    # Check if local model exists
    if os.path.exists(local_model_path) and os.path.isdir(local_model_path):
        logger.info("Loading model from local path...")
        model_to_load = local_model_path
    else:
        logger.info("Local model not found, will try to download from HuggingFace...")
        model_to_load = model_name

    logger.info(f"Resolved model path: {model_to_load}")
    
    try:
        # Initialize vLLM with the model
        llm = LLM(
            model=model_to_load,
            trust_remote_code=True,
            max_model_len=2048,  # Adjust based on your needs
            gpu_memory_utilization=0.8,
            dtype="float16"  # Use float16 for better performance
        )
        logger.info("Model loaded successfully!")
        return True
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        return False

def format_messages_for_qwen(messages: List[Message]) -> str:
    """Format messages for LLM model"""
    formatted_prompt = ""
    
    for message in messages:
        if message.role == "system":
            formatted_prompt += f"System: {message.content}\n\n"
        elif message.role == "user":
            formatted_prompt += f"User: {message.content}\n\n"
        elif message.role == "assistant":
            formatted_prompt += f"Assistant: {message.content}\n\n"
    
    formatted_prompt += "Assistant: "
    return formatted_prompt

@app.on_event("startup")
async def startup_event():
    """Initialize model on startup"""
    logger.info("Starting vLLM server...")
    success = initialize_model()
    if not success:
        logger.error("Failed to initialize model. Server may not work properly.")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": c.MODEL_NAME +" vLLM Server is running!", "model": model_name}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "model_loaded": llm is not None}

@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: ChatCompletionRequest):
    """Chat completions endpoint compatible with OpenAI API"""
    global llm
    
    if llm is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Format messages for the model
        prompt = format_messages_for_qwen(request.messages)
        
        # Set up sampling parameters
        sampling_params = SamplingParams(
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_tokens,
            stop=["User:", "System:"]  # Stop generation at these tokens
        )
        
        # Generate response
        outputs = llm.generate([prompt], sampling_params)
        
        if not outputs or not outputs[0].outputs:
            raise HTTPException(status_code=500, detail="No output generated")
        
        generated_text = outputs[0].outputs[0].text.strip()
        
        # Create response
        import time
        response = ChatCompletionResponse(
            id=f"chatcmpl-{int(time.time())}",
            created=int(time.time()),
            model=request.model,
            choices=[{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": generated_text
                },
                "finish_reason": "stop"
            }],
            usage={
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(generated_text.split()),
                "total_tokens": len(prompt.split()) + len(generated_text.split())
            }
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in chat completion: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting " + c.MODEL_NAME +" vLLM Server...")
    uvicorn.run(app, host="0.0.0.0", port=9999, log_level="info")