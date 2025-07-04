# Makefile for managing vLLM + FastAPI server

IMAGE_NAME = vllm_service
CONTAINER_NAME = vllm_container

build:
	docker-compose build --no-cache

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