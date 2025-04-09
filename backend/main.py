from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServer, MCPServerSse
from agents.model_settings import ModelSettings
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()
app.mount("/static", StaticFiles(directory="frontend"), name="static")

class ChatRequest(BaseModel):
    message: str

@app.on_event("startup")
async def startup_event():
    try:
        async with MCPServerSse(
            name="SSE Python Server",
            params={
                "url": "http://localhost:8001/sse",
            },
        ) as server:
            trace_id = gen_trace_id()
            with trace(workflow_name="OpenAI MCP Server", trace_id=trace_id):
                print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
                app.state.mcp_server = server
                await app.state.mcp_server.load()
    except Exception as e:
        print(f"Failed to connect to SSE server: {e}")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open("frontend/index.html", "r") as f:
        return HTMLResponse(content=f.read())


@app.post("/chat")
async def chat_endpoint(chat: ChatRequest, request: Request):
    try:
        mcp_server = request.app.state.mcp_server
        agent = Agent(
            name="Assistant",
            instructions="Use the tools to answer the questions.",
            mcp_servers=[mcp_server],
            model_settings=ModelSettings(tool_choice="required"),
        )

        print(f"Running: {chat.message}")
        result = await Runner.run(starting_agent=agent, input=chat.message)
        print(result.final_output)
        
        return {"response": result.final_output}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
