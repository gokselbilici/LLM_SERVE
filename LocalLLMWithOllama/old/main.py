import os
import yaml
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

# Load model↔quant mapping from config
with open("config.yml") as f:
    MODEL_MAP = yaml.safe_load(f)["models"]

app = FastAPI()

class ChatRequest(BaseModel):
    model: str        # e.g. "wizardlm"
    quantization: str # e.g. "q4_0"
    messages: list    # OpenAI-style [{role, content}, …]

@app.post("/chat")
async def chat(req: ChatRequest):
    # find full Ollama tag
    try:
        full_model = MODEL_MAP[req.model][req.quantization]
    except KeyError:
        raise HTTPException(400, "Unknown model or quantization")

    payload = {
        "model": full_model,
        "messages": req.messages
    }
    # forward to Ollama’s OpenAI-compatible API
    async with httpx.AsyncClient(base_url="http://localhost:11434") as client:
        resp = await client.post("/v1/chat/completions", json=payload)
        resp.raise_for_status()
        return resp.json()