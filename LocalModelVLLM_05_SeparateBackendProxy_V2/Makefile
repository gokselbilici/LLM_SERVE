up:
	docker network create llm_bridge || true
	cd vllm_serve && docker compose -f vllm-docker-compose.yml up -d
	cd ../controller_serve && docker compose -f controller_docker-compose.yml up -d

down:
	cd controller_serve && docker compose -f controller_docker-compose.yml down
	cd ../vllm_serve && docker compose -f vllm-docker-compose.yml down

logs:
	cd controller_serve && docker logs -f controller_llm_serving_api

logs-vllm:
	cd vllm_serve && docker logs -f vllm_openai_container
