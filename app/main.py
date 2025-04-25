
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routes.chat import router as chat_router
from routes.prompts import router as prompts_router
from routes.web import router as web_router
from routes.context import router as context_router
from core.assistant_factory import AssistantFactory
from services.openai_client import openai_client
from services.agent import load_tools, load_csv_resources
from core.state import app_state 
from core.config import setup_logging

setup_logging()

app = FastAPI()
app.mount("/static", StaticFiles(directory="frontend"), name="static")

app.include_router(chat_router)
app.include_router(prompts_router)
app.include_router(web_router)
app.include_router(context_router)

@app.on_event("startup")
async def startup_event():
    factory = AssistantFactory(openai_client)
    tools = await load_tools() 
    file_contents = await load_csv_resources()
    app_state.assistant_id = factory.create_family_activity_assistant(tools, file_contents)
    print(f"[startup] Assistant created with ID: {app_state.assistant_id}")