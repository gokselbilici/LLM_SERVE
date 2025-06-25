import os
import json
import requests
from typing import Optional, List, Dict, Generator
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from collections import defaultdict

app = FastAPI(title="Ollama API Wrapper")

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# In-memory session chat storage
chat_memory = defaultdict(list)

# ==== MODELS ==== #

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatInferenceRequest(BaseModel):
    CHAT_INPUT: Optional[List[ChatMessage]] = []
    model: Optional[str] = "qwen2.5:0.5b"
    stream: Optional[bool] = False
    session_id: Optional[str] = "default"

class ChatInferenceResponse(BaseModel):
    CHAT_OUTPUT: List[Dict[str, str]]

class GenerateRequest(BaseModel):
    model: str
    prompt: str
    stream: Optional[bool] = False

class PullRequest(BaseModel):
    name: str

class OpenAIChatMessage(BaseModel):
    role: str
    content: str

class OpenAIChatRequest(BaseModel):
    model: str
    messages: List[OpenAIChatMessage]
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.9
    stream: Optional[bool] = False

# ==== HELPERS ==== #

def format_chat_prompt(messages: List[ChatMessage], assistant_prefix: str = "Assistant") -> str:
    role_map = {"system": "System", "user": "User", "assistant": assistant_prefix}
    prompt_parts = [
        f"{role_map.get(m.role.lower(), 'User')}: {m.content.strip()}"
        for m in messages
    ]
    prompt_parts.append(f"{assistant_prefix}:")
    return "\n".join(prompt_parts)

def stream_ollama_response(payload: dict) -> Generator[str, None, None]:
    try:
        with requests.post(
            f"{OLLAMA_HOST}/api/generate", json=payload, stream=True, timeout=300
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode("utf-8"))
                        token = data.get("response", "")
                        if token:
                            yield token
                        if data.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        yield f"\n[Error] {str(e)}"

# ==== API ENDPOINTS ==== #

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/models")
async def list_models():
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/pull")
async def pull_model(request: PullRequest):
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/pull",
            json={"name": request.name},
            timeout=300,
            stream=True
        )
        response.raise_for_status()
        final_response = None
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode('utf-8'))
                    final_response = data
                    if data.get('status') == 'success':
                        break
                except json.JSONDecodeError:
                    continue
        return final_response or {"status": "completed", "message": f"Model {request.name} pulled"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.delete("/models/{model_name}")
async def delete_model(model_name: str):
    try:
        response = requests.delete(
            f"{OLLAMA_HOST}/api/delete",
            json={"name": model_name},
            timeout=30
        )
        response.raise_for_status()
        return {"message": f"Model {model_name} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/generate")
async def generate(request: GenerateRequest):
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={"model": request.model, "prompt": request.prompt, "stream": request.stream},
            timeout=120
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/chatinference")
async def chat_inference(request: ChatInferenceRequest):
    try:
        memory = chat_memory[request.session_id]
        full_history = memory + request.CHAT_INPUT

        prompt = format_chat_prompt(full_history)
        payload = {
            "model": request.model,
            "prompt": prompt,
            "stream": request.stream,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "stop": ["User:", "System:", "Assistant:"]
            }
        }

        if request.stream:
            return StreamingResponse(
                stream_ollama_response(payload),
                media_type="text/plain"
            )

        response = requests.post(f"{OLLAMA_HOST}/api/generate", json=payload, timeout=120)
        response.raise_for_status()
        reply = response.json().get("response", "").strip()

        updated = request.CHAT_INPUT + [ChatMessage(role="assistant", content=reply)]
        chat_memory[request.session_id] += updated

        full_response = [
            {"role": m.role, "content": m.content}
            for m in full_history + [ChatMessage(role="assistant", content=reply)]
        ]

        return ChatInferenceResponse(CHAT_OUTPUT=full_response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.post("/v1/chat/completions")
async def openai_compatible_chat(request: OpenAIChatRequest):
    try:
        messages = [ChatMessage(role=m.role, content=m.content) for m in request.messages]
        prompt = format_chat_prompt(messages)
        payload = {
            "model": request.model,
            "prompt": prompt,
            "stream": request.stream,
            "options": {
                "temperature": request.temperature,
                "top_p": request.top_p,
                "stop": ["User:", "System:", "Assistant:"]
            }
        }

        if request.stream:
            return StreamingResponse(
                stream_ollama_response(payload),
                media_type="text/plain"
            )

        response = requests.post(f"{OLLAMA_HOST}/api/generate", json=payload, timeout=120)
        response.raise_for_status()
        reply = response.json().get("response", "").strip()

        return {
            "id": "chatcmpl-openai-compatible",
            "object": "chat.completion",
            "model": request.model,
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": reply},
                "finish_reason": "stop"
            }]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI-compatible chat error: {str(e)}")