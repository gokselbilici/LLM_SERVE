import os

# The base URL for internal container-to-container communication
LLM_BACKEND_URL = os.getenv("LLM_API_HOST", "http://vllm_openai_container:8000")

# Optional: default system prompt if used
MAIN_SYSTEM_PROMPT = (
    "You are a helpful assistant. Provide concise, accurate, and friendly responses."
)