import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from typing import Optional
 
app = FastAPI(title="Ollama API Wrapper")

# Get Ollama host from environment variable, default to localhost for local development
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
 
class GenerateRequest(BaseModel):
    model: str
    prompt: str
    stream: Optional[bool] = False

class PullRequest(BaseModel):
    name: str
 
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/models")
async def list_models():
    """List available models"""
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to Ollama: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
@app.post("/generate")
async def generate(request: GenerateRequest):
    """Generate text using specified model"""
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": request.model,
                "prompt": request.prompt,
                "stream": request.stream
            },
            timeout=120  # Increased timeout for generation
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to Ollama: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/pull")
async def pull_model(request: PullRequest):
    """Pull a model to the local registry"""
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/pull",
            json={"name": request.name},
            timeout=300,  # 5 minute timeout for model pulling
            stream=True
        )
        response.raise_for_status()
        
        # Handle streaming response from Ollama
        final_response = None
        for line in response.iter_lines():
            if line:
                try:
                    import json
                    data = json.loads(line.decode('utf-8'))
                    final_response = data
                    if data.get('status') == 'success':
                        break
                except json.JSONDecodeError:
                    continue
        
        return final_response or {"status": "completed", "message": f"Model {request.name} pulled successfully"}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to Ollama: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/models/{model_name}")
async def delete_model(model_name: str):
    """Delete a model from the registry"""
    try:
        response = requests.delete(
            f"{OLLAMA_HOST}/api/delete",
            json={"name": model_name},
            timeout=30
        )
        response.raise_for_status()
        return {"message": f"Model {model_name} deleted successfully"}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to Ollama: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))