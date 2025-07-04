# PowerShell script to set up and run Qwen2.5-0.5B with vLLM
# Run this script from your project directory

Write-Host "=== Qwen2.5-0.5B vLLM Setup Script ===" -ForegroundColor Green

# Step 1: Create project directory
$projectDir = "qwen-vllm-server"
Write-Host "Creating project directory: $projectDir" -ForegroundColor Yellow

if (!(Test-Path $projectDir)) {
    New-Item -ItemType Directory -Path $projectDir
}

Set-Location $projectDir

# Step 2: Download model first (while online)
Write-Host "Downloading Qwen2.5-0.5B-Instruct model..." -ForegroundColor Yellow

# Create a temporary Python environment to download the model
python -m pip install huggingface_hub --quiet

# Download model to your specified directory
$modelPath = "D:\JYN\EZ\EGITIM\LLM_Model_Registry\TRANSFORMERS\Qwen2.5-0.5B-Instruct"
Write-Host "Model will be downloaded to: $modelPath" -ForegroundColor Cyan

python -c @"
from huggingface_hub import snapshot_download
import os

model_name = 'Qwen/Qwen2.5-0.5B-Instruct'
local_dir = r'$modelPath'

print(f'Downloading {model_name} to {local_dir}...')
os.makedirs(local_dir, exist_ok=True)

snapshot_download(
    repo_id=model_name,
    local_dir=local_dir,
    local_dir_use_symlinks=False,
    resume_download=True
)

print('Model download completed!')
"@

if ($LASTEXITCODE -eq 0) {
    Write-Host "Model downloaded successfully!" -ForegroundColor Green
} else {
    Write-Host "Model download failed. Please check your internet connection." -ForegroundColor Red
    exit 1
}

# Step 3: Build Docker image
Write-Host "Building Docker image..." -ForegroundColor Yellow
docker build -t qwen-vllm:latest .

if ($LASTEXITCODE -eq 0) {
    Write-Host "Docker image built successfully!" -ForegroundColor Green
} else {
    Write-Host "Docker build failed." -ForegroundColor Red
    exit 1
}

# Step 4: Run the container
Write-Host "Starting Qwen vLLM server..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "Server started successfully!" -ForegroundColor Green
    Write-Host "Server will be available at: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "Health check: http://localhost:8000/health" -ForegroundColor Cyan
    
    # Wait a moment and test the server
    Write-Host "Waiting for server to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
    
    Write-Host "Testing server..." -ForegroundColor Yellow
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
        Write-Host "Server is healthy: $($response | ConvertTo-Json)" -ForegroundColor Green
    }
    catch {
        Write-Host "Server might still be starting up. Check logs with: docker-compose logs -f" -ForegroundColor Yellow
    }
} else {
    Write-Host "Failed to start server." -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
Write-Host "To test the chat API, run:" -ForegroundColor Cyan
Write-Host @"
curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  --data '{
    "model": "Qwen/Qwen2.5-0.5B-Instruct",
    "messages": [
      {
        "role": "user",
        "content": "What is the capital of France?"
      }
    ]
  }'
"@ -ForegroundColor White

Write-Host "`nUseful commands:" -ForegroundColor Cyan
Write-Host "- View logs: docker-compose logs -f" -ForegroundColor White
Write-Host "- Stop server: docker-compose down" -ForegroundColor White
Write-Host "- Restart server: docker-compose restart" -ForegroundColor White