NETWORK=mcpnet

network:
	docker network create $(NETWORK) || true

build:
	docker build -t chat-mcp-client .

run: network
	docker run --rm --name mcp-client --network $(NETWORK) -p 8000:8000 --env-file .env chat-mcp-client

all: build run