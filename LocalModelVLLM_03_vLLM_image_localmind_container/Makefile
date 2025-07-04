# Makefile for vLLM Version 2 - Prebuilt Image Setup

CONTAINER_NAME = vllm_openai_container

up:
	docker-compose up

down:
	docker-compose down

logs:
	docker logs -f $(CONTAINER_NAME)

restart:
	make down && make up

status:
	docker ps -f name=$(CONTAINER_NAME)