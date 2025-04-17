import asyncio
import logging
import sys
import subprocess
from ping3 import ping

#from mcp.client.session import ClientSession
#from mcp.client.sse import  sse_client

from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServer, MCPServerSse
from agents.model_settings import ModelSettings

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str

app = FastAPI()
app.mount("/static", StaticFiles(directory="frontend"), name="static")
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(levelname)s:     [applogs] %(message)s')
    

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open("frontend/index.html", "r") as f:
        return HTMLResponse(content=f.read())
    

@app.post("/chat")
async def chat_endpoint(chat: ChatRequest):
    try:
        #logging.info("try to connect...")
        #async with sse_client(
        #    url="http://mcp-server:8001/sse"
        #) as (read, write):
        #    logging.info("Connected.")
        #    async with ClientSession(read, write) as session:
        #        await session.initialize()

        #        #List available prompts
        #        tools = await session.list_tools()
        #        logging.info(tools)

        async with MCPServerSse(
            name="SSE Python Server",
            params={
                "url": "http://mcp-server:8001/sse",
            },
        ) as mcp_server:
            trace_id = gen_trace_id()
            with trace(workflow_name="SSE Example", trace_id=trace_id):
                print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
                agent = Agent(
                    name="Assistant",
                    instructions="Use the tools to answer the questions.",
                    mcp_servers=[mcp_server],
                    model_settings=ModelSettings(tool_choice="required"),
                )
                result = await Runner.run(starting_agent=agent, input=chat.message)

        return {"response": result.final_output}

    except Exception as e:
        logging.info(f"Exception: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
    