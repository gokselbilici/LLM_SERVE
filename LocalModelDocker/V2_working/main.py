import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from typing import Optional, List, Dict, Any
 
app = FastAPI(title="Ollama API Wrapper")

# Get Ollama host from environment variable, default to localhost for local development
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
 
class GenerateRequest(BaseModel):
    model: str
    prompt: str
    stream: Optional[bool] = False

class PullRequest(BaseModel):
    name: str

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatInferenceRequest(BaseModel):
    CHAT_INPUT: List[ChatMessage]
    model: Optional[str] = "qwen2.5:0.5b"  # Default model, can be overridden

class ChatInferenceResponse(BaseModel):
    CHAT_OUTPUT: List[Dict[str, str]]
 
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

@app.post("/chatinference")
async def chat_inference(request: ChatInferenceRequest):
    """
    Chat inference endpoint that maintains conversation history
    Takes a list of chat messages and returns the complete conversation with assistant response
    """
    try:
        # Convert chat messages to a prompt format that Ollama can understand
        prompt_parts = []
        
        for message in request.CHAT_INPUT:
            if message.role == "system":
                prompt_parts.append(f"System: {message.content}")
            elif message.role == "user":
                prompt_parts.append(f"User: {message.content}")
            elif message.role == "assistant":
                prompt_parts.append(f"Assistant: {message.content}")
        
        # Add instruction for the assistant to respond
        prompt_parts.append("Assistant:")
        
        # Join all parts into a single prompt
        full_prompt = "\n".join(prompt_parts)
        
        # Make request to Ollama
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": request.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "stop": ["User:", "System:"]  # Stop generation at next role
                }
            },
            timeout=120
        )
        response.raise_for_status()
        
        # Get the generated response
        ollama_response = response.json()
        assistant_content = ollama_response.get("response", "").strip()
        
        # Build the complete chat output
        chat_output = []
        
        # Add all input messages to output
        for message in request.CHAT_INPUT:
            chat_output.append({
                "role": message.role,
                "content": message.content
            })
        
        # Add the assistant's response
        chat_output.append({
            "role": "assistant",
            "content": assistant_content
        })
        
        return ChatInferenceResponse(CHAT_OUTPUT=chat_output)
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to Ollama: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat inference error: {str(e)}")