import asyncio
import logging
import sys
import subprocess
from fastapi import FastAPI
from mcp.client.session import ClientSession
from mcp.client.sse import  sse_client
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str

#@asynccontextmanager
#async def lifespan(app: FastAPI):
#    persistent_client = MultiServerMCPClient(servers_config)
#    await persistent_client.__aenter__()
#    app.state.persistent_client = persistent_client
#    yield
#    await app.state.persistent_client.__aexit__(None, None, None)

#app = FastAPI(lifespan=lifespan)
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
        logging.info("try to connect...")
        async with sse_client(
            url="http://localhost:8001/sse"
        ) as (read, write):
            logging.info("Connected.")
            async with ClientSession(read, write) as session:
                await session.initialize()

                #List available prompts
                tools = await session.list_tools()
                logging.info(tools)
        
        #agent = Agent(
        #    name="Assistant",
        #    instructions="Use the tools to answer the questions.",
        #    mcp_servers=[mcp_server],
        #    model_settings=ModelSettings(tool_choice="required"),
        #)

        #print(f"Running: {chat.message}")
        #result = await Runner.run(starting_agent=agent, input=chat.message)
        #print(result.final_output)
        
        return {"response": "OK"}
    except Exception as e_group:
        errors = [str(e) for e in e_group.exceptions]
        return JSONResponse(status_code=500, content={"error": errors})
    