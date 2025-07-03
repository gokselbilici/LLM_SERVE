# Qwen2.5-0.5B vLLM Server

This project runs a **FastAPI-based OpenAI-compatible LLM server** using **vLLM** and **Qwen2.5-0.5B-Instruct** model from Hugging Face. The model is downloaded and served locally with GPU acceleration in a Docker container.

---

## 🔧 Features

- ✅ OpenAI-style `/v1/chat/completions` endpoint
- ✅ Docker & Docker Compose with GPU support
- ✅ Custom FastAPI server with health checks
- ✅ Uses Hugging Face `snapshot_download()` to download and manage models
- ✅ Environment-configurable paths and model name

---

## 🗂️ Project Structure

```
.
├── Dockerfile
├── docker-compose.yml
├── download_model.py
├── main.py
├── constants.py
├── requirements.txt
├── Makefile
└── README.md
```

---

## 🚀 Quick Start

### 1. 📥 Download the Model

You can run this once to download the model locally:

```bash
python download_model.py "Qwen/Qwen2.5-0.5B-Instruct"
```

It will save to:
```
D:\JYN\EZ\EGITIM\LLM_Model_Registry\HuggingFaceRepo\app\models\models--Qwen--Qwen2.5-0.5-Instruct
```

---

### 2. 🐳 Build & Run the Container

You can use Docker Compose:

```bash
make build
make up
```

Or directly:

```bash
docker-compose up --build
```

---

## 📡 API Endpoints

- `GET /` — Root health message
- `GET /health` — Health check status
- `POST /v1/chat/completions` — OpenAI-compatible completion endpoint

#### Example request (JSON):

```json
{
  "model": "Qwen/Qwen2.5-0.5B-Instruct",
  "messages": [
    {"role": "user", "content": "What is the capital of Japan?"}
  ]
}
```

---

## 🖥️ Port Mapping

| Host Port | Container Port | Description               |
|-----------|----------------|---------------------------|
| `9999`    | `9999`         | FastAPI server (uvicorn)  |

---

## 🧠 Environment Variables

Defined in `docker-compose.yml`:

- `MODEL_PATH=/app/models`
- `HF_HOME=/app/cache`
- `CUDA_VISIBLE_DEVICES=0`

---

## ⚙️ Makefile Commands

See [`Makefile`](Makefile) for CLI shortcuts:

```bash
make build     # Build Docker image
make up        # Start the container
make down      # Stop and remove the container
make logs      # Tail logs from container
```

---

## 🧪 Health Check

```bash
curl http://localhost:9999/health
```

Returns:

```json
{
  "status": "healthy",
  "model_loaded": true
}
```

---

## 📜 License

MIT