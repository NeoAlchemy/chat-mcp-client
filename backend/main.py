import logging
import sys
import os
from ping3 import ping

from mcp.client.session import ClientSession
from mcp.client.sse import  sse_client

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
        if chat.type=="tools":
            result = await openai_agent_weather_tools(chat.message)

        elif chat.type=="resources":
            result = await openai_agent_book_resources(chat.message)


        return {"response": result.final_output}

    except Exception as e:
        logging.info(f"Exception: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})



async def openai_agent_weather_tools(message: str) -> dict:
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
            return await Runner.run(starting_agent=agent, input=message)

async def openai_agent_book_resources(message: str) -> dict:
        async with sse_client( url="http://mcp-server:8001/sse" ) as (read, write):
            logging.info("Connected.")
            async with ClientSession(read, write) as session:
                await session.initialize()
                resources_result = await session.list_resources()
                logging.info(f"what are the resources {resources_result}")
                openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

                first_uri = resources_result.resources[0].uri
                read_result = await session.read_resource(uri=first_uri)
                text_content = read_result.contents[0].text

                chat = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": f"If asked about Rulebooks reference your answers from the following content: \n\n{ text_content }"},
                        {"role": "user",   "content": f"{ message }"}
                    ],
                    max_tokens=300
                )

                # Extract the assistant’s reply
                summary = chat.choices[0].message.content
                logging.info(f"summary: {summary}")
                return {"final_output": summary}