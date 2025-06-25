# LLM_SERVE 🚀

**LLM_SERVE** is a lightweight, high-performance Python server framework for deploying large language model (LLM) inference endpoints. Easily host LLMs (e.g., OpenAI GPT‑3.5/4, LLaMA, custom models) via REST or WebSocket APIs, with built-in support for load balancing, batching, streaming, and modular deployment.

---

## 🚀 Features

- **Model Flexibility**  
  Supports native & OpenAI-hosted models, including off‑line and online setups.

- **API Interface**  
  - **RESTful HTTP** endpoints (`/v1/chat`, `/v1/completions`)  
  - **Streaming responses** via Server‑Sent Events (SSE)

- **Concurrency & Performance**  
  Asynchronous architecture with request batching, throttling, and optional thread/process pools.

- **Scalable Deployment**  
  Easily containerized via Docker; compatible with Kubernetes, AWS Lambda / ECS, or custom Docker environments.

- **Configurable & Extensible**  
  Plug in custom authentication, logging, caching, rate limiting, transformers, middlewares.

- **Observability**  
  Built-in Prometheus metrics & optional OpenTelemetry tracing for monitoring throughput, latency, error rates.

---

## 🔧 Quickstart

**1. Clone and install dependencies**

```bash
git clone https://github.com/gokselbilici/LLM_SERVE.git
cd LLM_SERVE
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**2. Configure your model**

Edit `config.yaml`:

```yaml
provider: openai           # or "local", "docker"
model_name: gpt-4          # e.g., gpt-3.5-turbo, llama-2-7b
batch_size: 8
max_tokens: 512
timeout_s: 60
stream: true
```

**3. Run the server**

```bash
uvicorn llm_serve.main:app --host 0.0.0.0 --port 8000
```

**4. Call your LLM endpoint**

```bash
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
        "messages": [{"role": "user", "content": "Hello, world!"}],
        "stream": false
      }'
```

---

## 🧩 Endpoints

### `POST /v1/chat`
Chat-style interaction.  
**Request Body (JSON)**:

```json
{
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."}
  ],
  "stream": false
}
```

**Response** (if `stream: false`):

```json
{
  "id": "chatcmpl-...",
  "choices": [
    {"message": {"role": "assistant", "content": "..."}}
  ],
  "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
}
```

If `stream: true`, uses SSE for incremental `chunk` events.

### `POST /v1/completions`
Classic completion endpoint. Similar interface with `prompt` and generation parameters.

---

## ⚙️ Configuration

`config.yaml` supports:

| Key              | Type     | Description                              |
|------------------|----------|------------------------------------------|
| provider         | string   | LLM backend: `openai`, `local`, etc.    |
| model_name       | string   | Model identifier                         |
| api_key          | string   | For hosted models (e.g. OpenAI)         |
| batch_size       | integer  | Number of parallel requests              |
| max_tokens       | integer  | Max tokens to generate per request       |
| temperature      | float    | Sampling temperature                     |
| stream           | boolean  | Enable real-time streaming               |
| timeout_s        | integer  | Max inference timeout in seconds         |

Supports overriding via environment variables (e.g., `MODEL_NAME`, `BATCH_SIZE`, `API_KEY`).

---

## 🛠️ Advanced Usage

- **Docker**  
  Build and run:

  ```bash
  docker build -t llm_serve:latest .
  docker run -p 8000:8000 llm_serve:latest
  ```

- **Kubernetes Helm**  
  A `helm/` chart is included—modify `values.yaml` and deploy.

- **Middleware**  
  Customize by creating your own in `llm_serve/middleware.py`.

- **Metrics & Logging**  
  `/metrics` endpoint for Prometheus.  
  Logging via `uvicorn` format or plug in OpenTelemetry.

---

## ✅ Testing

```bash
pytest -q
```

Tests cover endpoint sanity, batching, streaming, error handling, and mock LLM backends.

---

## 🚧 Roadmap

- [ ] Multi-model support  
- [ ] GPU-backed local inference (e.g., `transformers`, `accelerate`)  
- [ ] Role-based auth / API key management  
- [ ] Rate limiting & quota enforcement per user

---

## ❤️ Contributing

1. Fork the repo  
2. Create a feature branch  
3. Submit a pull request  
4. Ensure tests pass and new functionality is covered

All contributions are welcome!

---

## 📄 License

[MIT License](./LICENSE)

---

## 📬 Questions?

Open an [issue](https://github.com/gokselbilici/LLM_SERVE/issues) or reach out to @goksel on GitHub.

---

*Made with ❤️ by Göksel Bilici*
