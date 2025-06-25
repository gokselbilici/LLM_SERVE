# Use a lightweight Linux base
FROM ubuntu:22.04

# Install Ollama and Python
RUN apt-get update && \
    apt-get install -y curl ca-certificates python3 python3-pip && \
    curl -fsSL https://ollama.com/install.sh | bash   # install Ollama :contentReference[oaicite:1]{index=1}

WORKDIR /app

# Install FastAPI and HTTP client
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Add your API code
COPY main.py .

# Entrypoint: start Ollama server in background, then FastAPI
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 11434 8000

CMD ["./entrypoint.sh"]