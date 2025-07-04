# Qwen2.5-0.5B vLLM Server (Version 2 — Prebuilt Docker Image)

This version runs the **Qwen2.5-0.5B-Instruct** model using the **official prebuilt vLLM Docker image** with GPU acceleration. The model is loaded from a local Hugging Face snapshot, and served via an OpenAI-compatible API.

---

## 📦 Steps to Run

### 1️⃣ Pull the vLLM Docker Image

```bash
docker pull vllm/vllm-openai:latest
```

---

### 2️⃣ Create the `docker-compose.yml`

```yaml
version: "3.8"

services:
  vllm_api:
    image: vllm/vllm-openai:latest
    container_name: vllm_openai_container
    runtime: nvidia
    ports:
      - "9999:8000"
    volumes:
      - "D:/JYN/EZ/EGITIM/LLM_Model_Registry/HuggingFaceRepo/app/models:/root/.cache/huggingface"
    environment:
      - HUGGING_FACE_HUB_TOKEN=hf_xxx_optional
    command: >
      --model /root/.cache/huggingface/models--Qwen--Qwen2.5-0.5B-Instruct
      --gpu-memory-utilization 0.6
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

---

### 3️⃣ Run the Server

```bash
docker-compose up
```

If successful, the API server will run on:  
```
http://localhost:9999
```

---

## 🧪 Test the API

### Endpoint:
```
POST http://localhost:9999/v1/chat/completions
```

### Sample Request:
```json
{
  "messages": [
    {"role": "user", "content": "Hello, what can you do?"}
  ]
}
```

---

## ⚙️ Makefile Commands

```bash
make up        # Start the vLLM container
make down      # Stop and remove the container
make logs      # Tail logs from the container
make restart   # Restart the container
make status    # Check container status
```

---

## ✅ Notes

- The model must be downloaded already to:
  ```
  D:/JYN/EZ/EGITIM/LLM_Model_Registry/HuggingFaceRepo/app/models/models--Qwen--Qwen2.5-0.5B-Instruct
  ```
- `config.json` must be present inside that folder.
- GPU memory utilization is limited to `60%` to prevent OOM errors on 8 GB cards.

---

## 🧠 About

- Model: Qwen/Qwen2.5-0.5B-Instruct
- Runtime: NVIDIA GPU
- API: OpenAI-compatible (`/v1/chat/completions`)
- Framework: vLLM (Docker image `vllm/vllm-openai`)