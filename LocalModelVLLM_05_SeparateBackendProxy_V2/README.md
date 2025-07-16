# 🧠 Local LLM Serving with vLLM + FastAPI Controller

This project demonstrates how to serve a language model (Qwen2.5-0.5B-Instruct) using `vLLM` in one container, and a FastAPI-based controller in a separate container. The two communicate over a shared Docker network with enterprise-grade features including health monitoring, rate limiting, and enhanced error handling.

## 📁 Project Structure

```
LLM_SERVE/
├── controller_serve/
│   ├── controller_docker-compose.yml
│   ├── Dockerfile
│   ├── main.py
│   ├── constants.py
│   ├── requirements.txt
│   └── logs/                          # Auto-created log directory
├── vllm_serve/
│   ├── vllm_docker-compose.yml
│   └── .env                           # Environment variables (optional)
└── README.md
```

---

## ✨ Features

### 🔧 Core Features
- **OpenAI-compatible API** endpoints
- **Dockerized microservices** architecture
- **Health monitoring** with automatic checks
- **Rate limiting** (100 requests/minute per IP)
- **Request tracking** with unique request IDs
- **Comprehensive logging** with structured format
- **Error handling** with proper HTTP status codes

### 📊 Monitoring & Observability
- Health check endpoints (`/health`, `/metrics`)
- Backend connectivity monitoring
- Request/response logging with token usage
- Docker health checks with auto-recovery

### 🛡️ Production Ready
- Non-root Docker containers for security
- Configurable timeouts and retry logic
- CORS support for web applications
- Environment-based configuration
- Graceful startup and shutdown

---

## 🚀 Quick Start

### 1. Prerequisites
- Docker and Docker Compose installed
- NVIDIA Docker runtime (for GPU support)
- Downloaded model in the specified path

### 2. Create the Shared Docker Network
```bash
docker network create llm_bridge
```

### 3. Start the vLLM Backend (Model Server)
```bash
cd vllm_serve
docker compose -f vllm_docker-compose.yml up -d
```

### 4. Wait for Model Loading (Optional)
```bash
# Check if vLLM is ready
curl http://localhost:9990/v1/models

# Or check container health
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### 5. Start the FastAPI Controller
```bash
cd ../controller_serve
docker compose -f controller_docker-compose.yml up
```

---

## 🔧 Configuration

### Environment Variables

#### Controller Service (`controller_docker-compose.yml`)
```yaml
environment:
  - LLM_API_HOST=http://vllm_openai_container:8000  # Backend URL
  - LOG_LEVEL=INFO                                   # DEBUG, INFO, WARNING, ERROR
  - RATE_LIMIT_PER_MINUTE=100                       # Requests per minute per IP
  - BACKEND_TIMEOUT=60.0                            # Backend request timeout
  - CONTROLLER_HOST=0.0.0.0                         # Controller bind host
  - CONTROLLER_PORT=9999                            # Controller bind port
```

#### vLLM Service (`.env` file - optional)
```env
MODEL_PATH=/root/.cache/huggingface/models--Qwen--Qwen2.5-0.5B-Instruct
GPU_MEMORY_UTIL=0.6
VLLM_HOST=0.0.0.0
VLLM_PORT=8000
```

### Model Path Configuration
Update the volume mount in `vllm_docker-compose.yml`:
```yaml
volumes:
  - "YOUR_MODEL_PATH:/root/.cache/huggingface"
```

---

## 📡 API Endpoints

### Health & Monitoring
| Method | Path | Description | Response |
|--------|------|-------------|----------|
| GET | `/` | Basic health check | Service status |
| GET | `/health` | Detailed health check | Service + backend health |
| GET | `/metrics` | Basic metrics | Health metrics |

### Model Operations
| Method | Path | Description | Response |
|--------|------|-------------|----------|
| GET | `/v1/models` | Lists available models | Model metadata |
| POST | `/v1/chat/completions` | Chat completion | Generated response |

---

## 🧪 Testing the Setup

### Basic Health Check
```bash
# Check controller health
curl http://localhost:9999/health

# Check vLLM directly
curl http://localhost:9990/v1/models
```

### Chat Completion Request
```bash
curl -X POST \
  'http://localhost:9999/v1/chat/completions' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'X-Request-ID: test-123' \
  -d '{
    "messages": [
      { "role": "user", "content": "Selamlar" },
      { "role": "assistant", "content": "Selam! Size nasıl yardımcı olabilirim?" },
      { "role": "user", "content": "Kısa bir hikaye anlatabilir misin?" }
    ],
    "temperature": 0.7,
    "top_p": 0.8,
    "max_tokens": 512
  }'
```

### Expected Response
```json
{
  "id": "chatcmpl-ba22556957b946558e6a42a4f28f3f04",
  "object": "chat.completion",
  "created": 1752671982,
  "model": "/root/.cache/huggingface/models--Qwen--Qwen2.5-0.5B-Instruct",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Üzgünüm, ben bir AI model değilim ve bu konuda bilgi almak mümkün değil. Ancak, size nasıl yardımcı olabileceğimi belirtmek için daha fazla detaylayabilirsiniz."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 63,
    "total_tokens": 111,
    "completion_tokens": 48
  }
}
```

---

## 🔍 Monitoring & Troubleshooting

### View Logs
```bash
# Controller logs
docker logs controller_llm_serving_api -f

# vLLM logs
docker logs vllm_openai_container -f

# Or check log files
tail -f controller_serve/logs/controller.log
```

### Check Container Health
```bash
# View container status
docker ps --format "table {{.Names}}\t{{.Status}}"

# Detailed health information
docker inspect vllm_openai_container --format='{{.State.Health.Status}}'
```

### Debug Network Issues
```bash
# Test network connectivity
docker network ls
docker network inspect llm_bridge

# Test internal communication
docker exec controller_llm_serving_api curl -f http://vllm_openai_container:8000/v1/models
```

---

## 🚨 Common Issues & Solutions

### 1. Model Loading Errors
```bash
# Check model path exists
ls -la "YOUR_MODEL_PATH/models--Qwen--Qwen2.5-0.5B-Instruct"

# Verify permissions
docker exec vllm_openai_container ls -la /root/.cache/huggingface/
```

### 2. GPU Not Detected
```bash
# Install nvidia-docker2
# Check GPU availability
nvidia-smi
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

### 3. Port Conflicts
```bash
# Check port usage
netstat -tulpn | grep :9999
netstat -tulpn | grep :9990

# Change ports in docker-compose files if needed
```

### 4. Rate Limiting
```bash
# Test rate limiting
for i in {1..5}; do curl -s http://localhost:9999/health; done
```

---

## 🔄 Alternative Deployment Options

### Single Docker Compose File
For simpler management, use the combined approach:
```bash
# Use combined_docker-compose.yml
docker compose -f combined_docker-compose.yml up
```

### Production Deployment
```bash
# Use detached mode
docker compose -f vllm_docker-compose.yml up -d
docker compose -f controller_docker-compose.yml up -d

# Check status
docker compose -f vllm_docker-compose.yml ps
docker compose -f controller_docker-compose.yml ps
```

---

## 📚 API Documentation

### Request Headers
- `Content-Type: application/json` (required)
- `X-Request-ID: your-id` (optional, for tracking)

### Rate Limiting
- Default: 100 requests per minute per IP
- Configurable via `RATE_LIMIT_PER_MINUTE` environment variable
- Returns HTTP 429 when exceeded

### Error Codes
- `400`: Bad Request (invalid input)
- `429`: Rate limit exceeded
- `502`: Backend unavailable
- `503`: Service unavailable
- `504`: Backend timeout

---

## 🛠️ Development

### Adding New Features
1. Update `main.py` for new endpoints
2. Add configuration in `constants.py`
3. Update Docker Compose files if needed
4. Test with the provided curl examples

### Custom Model
1. Download your model to the volume path
2. Update `MODEL_PATH` in `vllm_docker-compose.yml`
3. Restart the vLLM container

---

## 📈 Performance Tuning

### GPU Memory Optimization
```yaml
# In vllm_docker-compose.yml
command: >
  --model /path/to/model
  --gpu-memory-utilization 0.8  # Increase for more GPU memory
  --max-model-len 4096          # Adjust max sequence length
```

### Concurrent Requests
```yaml
# In controller environment
- RATE_LIMIT_PER_MINUTE=200    # Increase rate limit
- BACKEND_TIMEOUT=120.0        # Increase timeout for complex requests
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 👨‍💻 Author

**Made with ❤️ by Göksel Bilici**

---

## 🙏 Acknowledgments

- [vLLM](https://github.com/vllm-project/vllm) for the high-performance inference engine
- [FastAPI](https://fastapi.tiangolo.com/) for the modern web framework
- [Qwen](https://huggingface.co/Qwen) for the language model