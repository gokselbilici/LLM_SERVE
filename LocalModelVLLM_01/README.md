# Qwen2.5-0.5B vLLM Server (GPU-Powered via Docker)

This project serves the **Qwen2.5-0.5B-Instruct** model using [vLLM](https://github.com/vllm-project/vllm) and a **FastAPI** backend inside a GPU-enabled Docker container. It supports **OpenAI-compatible chat completions**.

---

## 🚀 Features

- ✅ OpenAI-style endpoint: `/v1/chat/completions`
- ✅ GPU acceleration via CUDA 12.8
- ✅ Model loaded from local Hugging Face snapshot
- ✅ Docker & Docker Compose with NVIDIA runtime
- ✅ Health-check endpoint
- ✅ Pre-configured with `torch`, `transformers`, `vllm`, and FastAPI

---

## 📁 Project Structure

```
.
├── Dockerfile               # Builds the container
├── docker-compose.yml       # Runs the server with GPU
├── requirements.txt         # Python dependencies
├── main.py                  # FastAPI + vLLM inference server
├── download_model.py        # Downloads model from Hugging Face
├── constants.py             # Local model path & model name
├── Makefile                 # CLI commands for Docker tasks
└── README.md
```

---

## ⚙️ Setup Steps

### Step 1 – 🔽 Download the Model (Optional if already mounted)

```bash
python download_model.py
```

> This downloads Qwen2.5-0.5B-Instruct to:
> `D:/JYN/EZ/EGITIM/LLM_Model_Registry/HuggingFaceRepo/app/models`

---

### Step 2 – 🐳 Build & Run

You can use `make` or plain Docker:

```bash
# Using Makefile
make build     # Builds the Docker image
make up        # Starts the container
```

OR manually:

```bash
docker build -t vllm_service:latest .
docker-compose build --no-cache
docker-compose up
```

---

## 📡 API Usage

### 🔗 Base URL

```
http://localhost:9999
```

### ✅ Endpoints

| Method | Path                  | Description              |
|--------|-----------------------|--------------------------|
| GET    | `/`                   | Root message             |
| GET    | `/health`             | Health + model status    |
| POST   | `/v1/chat/completions`| OpenAI-style chat endpoint |

---

### 🧪 Example Request

**URL:**
```
POST http://localhost:9999/v1/chat/completions
```

**Request Body:**
```json
{
  "model": "Qwen/Qwen2.5-0.5B-Instruct",
  "messages": [
    {
      "role": "user",
      "content": "Hello, who are you?"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 512,
  "top_p": 0.9
}
```

---

## 🖥️ Port Mapping

| Host Port | Container Port | Service         |
|-----------|----------------|------------------|
| `9999`    | `9999`         | FastAPI (Uvicorn) |

---

## 🧠 Environment Variables

Defined in `docker-compose.yml`:

- `MODEL_PATH=/app/models`
- `HF_HOME=/app/cache`
- `CUDA_VISIBLE_DEVICES=0`

---

## 🔧 Makefile Commands

```bash
make build     # Build Docker image (docker-compose build)
make up        # Start the container (detached)
make down      # Stop and remove the container
make logs      # View real-time logs
make restart   # Restart container
make status    # Check running container status
```

---

## ✅ Health Check

```bash
curl http://localhost:9999/health
```

Expected response:
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

---

## 📜 License

MIT