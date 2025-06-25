from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OLLAMA_API = "http://ollama:11434/api"
MODEL_NAME = os.getenv("MODEL_NAME", "qwen3:0.6b")

app = FastAPI(title="Ollama API Wrapper")

class GenerateRequest(BaseModel):
    model: Optional[str] = MODEL_NAME
    prompt: str
    stream: Optional[bool] = False

@app.get("/models")
async def list_models():
    try:
        response = requests.get(f"{OLLAMA_API}/tags")
        if response.status_code == 200:
            return response.json()
        raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/pull")
async def pull_model():
    try:
        response = requests.post(f"{OLLAMA_API}/pull", json={"name": MODEL_NAME})
        if response.status_code == 200:
            return response.json()
        raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate")
async def generate(request: GenerateRequest):
    try:
        payload = {
            "model": request.model,
            "prompt": request.prompt,
            "stream": request.stream
        }

        response = requests.post(
            f"{OLLAMA_API}/generate",
            json=payload,
            stream=request.stream
        )

        if request.stream:
            def stream_response():
                for line in response.iter_lines():
                    if line:
                        yield line.decode("utf-8") + "\n"

            return StreamingResponse(stream_response(), media_type="text/event-stream")

        else:
            if response.status_code == 200:
                return response.json()
            raise HTTPException(status_code=response.status_code, detail=response.text)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
