# chat-client-mcp
Just a test of a chat client that is using MCP
## Run App
docker build -t chat-client-mcp .
docker run -d -p 8000:8000 --env-file .env chat-client-mcp
