import os
from typing import Optional

# Backend configuration
LLM_BACKEND_URL: str = os.getenv("LLM_API_HOST", "http://vllm_openai_container:8000")
CONTROLLER_PORT: int = int(os.getenv("CONTROLLER_PORT", "9999"))
CONTROLLER_HOST: str = os.getenv("CONTROLLER_HOST", "0.0.0.0")

# Timeout configuration
BACKEND_TIMEOUT: float = float(os.getenv("BACKEND_TIMEOUT", "60.0"))
HEALTH_CHECK_TIMEOUT: float = float(os.getenv("HEALTH_CHECK_TIMEOUT", "10.0"))

# Logging configuration
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT: str = "%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"

# Rate limiting (requests per minute)
RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))

# API configuration
API_VERSION: str = "v1"
SERVICE_NAME: str = "llm-controller"