# Makefile for managing vLLM + FastAPI server

IMAGE_NAME = vllm-qwen
CONTAINER_NAME = qwen-vllm-server

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker logs -f $(CONTAINER_NAME)

restart:
	make down && make up

status:
	docker ps -f name=$(CONTAINER_NAME)
