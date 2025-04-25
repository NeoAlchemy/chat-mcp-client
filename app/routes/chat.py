
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from models.schemas import ChatRequest
from services.openai_client import openai_agent_service

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        response = await openai_agent_service.handle_message(request.message)
        return {"response": response}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
