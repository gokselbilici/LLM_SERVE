# 🧠 Local LLM Serving with vLLM + FastAPI Controller

This project demonstrates how to serve a language model (Qwen2.5-0.5B-Instruct) using `vLLM` in one container, and a FastAPI-based controller in a separate container. The two communicate over a shared Docker network.

## 📁 Project Structure

```
LLM_SERVE/
├── controller_serve/
│   ├── controller_docker-compose.yml
│   ├── Dockerfile
│   ├── main.py
│   ├── constants.py
│   ├── requirements.txt
├── vllm_serve/
│   └── vllm-docker-compose.yml
```

---

## 🚀 Usage Instructions

### 1. Create the Shared Docker Network
```bash
docker network create llm_bridge
```

### 2. Start the vLLM Backend (Model Server)
```bash
cd vllm_serve
docker compose -f vllm-docker-compose.yml up
```

### 3. Start the FastAPI Controller
```bash
cd ../controller_serve
docker compose -f controller_docker-compose.yml up
```

---

## 📡 Test the Setup

### Sample `curl` Request:
```bash
curl -X 'POST' \
  'http://localhost:9999/v1/chat/completions' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "messages": [
      { "role": "user", "content": "Selamlar canım" },
      { "role": "assistant", "content": "Selam! Size nasıl yardımcı olabilirim?" },
      { "role": "user", "content": "Beni tanıyorsan adımı söyle" }
    ],
    "temperature": 0.7,
    "top_p": 0.8,
    "max_tokens": 512
  }'
```

### Expected Response Snippet:
```json
{
  "id": "chatcmpl-...",
  "model": "...",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Üzgünüm, ben bir AI model değilim ve bu konuda bilgi almak mümkün değil..."
      }
    }
  ]
}
```

---

## ⚠️ Notes

- Make sure the model is already downloaded to your volume path:
  `D:/JYN/EZ/EGITIM/LLM_Model_Registry/HuggingFaceRepo/app/models`

- You can change `LLM_API_HOST` in `controller_docker-compose.yml` or `.env` to point to a different backend.

---

## ✅ Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Health check |
| GET | `/v1/models` | Lists available models |
| POST | `/v1/chat/completions` | Sends a chat prompt to the model |

---

Made with ❤️ by Göksel Bilici
