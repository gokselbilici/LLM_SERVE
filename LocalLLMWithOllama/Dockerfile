# Use Microsoft's lightweight Python 3.11 image
FROM mcr.microsoft.com/mirror/docker/library/python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies from PyPI
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Expose FastAPI port (Docker Compose maps 9999:9999)
EXPOSE 9999

# Start FastAPI app via Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9999"]