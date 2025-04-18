import logging
import sys
import os
from ping3 import ping

#from mcp.client.session import ClientSession
#from mcp.client.sse import  sse_client

from openai import OpenAI


from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServer, MCPServerSse
from agents.model_settings import ModelSettings

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    type: str

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

        # ======== TOOLS ===========
        if chat.type=="tools":
            async with MCPServerSse(
                name="SSE Python Server",
                params={
                    "url": "http://mcp-server:8001/sse",
                },
            ) as mcp_server:
                trace_id = gen_trace_id()
                with trace(workflow_name="Weather Tool", trace_id=trace_id):
                    print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")  
                    agent = Agent(
                        name="Assistant",
                        instructions="Only use tools when absolutely necessary to complete \
                            the user's request. If the answer is available in context or \
                            from your training, respond directly without tools.",
                        mcp_servers=[mcp_server],
                        model_settings=ModelSettings(tool_choice="auto"),
                    )
                    result = await Runner.run(starting_agent=agent, input=chat.message)



        elif chat.type=="resources":
            logging.info("===== RESOURCES ======")
            # ========== RESOURCES ========
            resources_result = await mcp_server.list_resources()
            openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            first_uri = resources_result.resources[0].uri
            read_result = await mcp_server.read_resource(uri=first_uri)
            text_content = read_result.contents[0].text

            chat = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"If asked about Rulebooks reference your answers from the following content: \n\n{ text_content }"},
                    {"role": "user",   "content": f"{ chat.message }"}
                ],
                max_tokens=300
            )

            # Extract the assistant’s reply
            summary = chat.choices[0].message.content
            logging.info(f"summary: {summary}")
            result= {"final_output": summary}


        return {"response": result.final_output}

    except Exception as e:
        logging.info(f"Exception: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
    