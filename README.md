# chat-client-mcp
Just a test of a chat client that is using MCP

## Setup
1. Download Docker Desktop
2. For Mac
    a. add $HOME/.docker/bin to PATH

## Setup
1. Clone the repo


## Run App
```sh
docker build -t chat-client-mcp .
docker run -d -p 8000:8000 --env-file .env chat-client-mcp
```
