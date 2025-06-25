#!/bin/sh
# start Ollama’s REST API server (default port 11434)
ollama serve &
# start our FastAPI wrapper
exec uvicorn main:app --host 0.0.0.0 --port 8000