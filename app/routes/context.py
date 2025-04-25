from fastapi import APIRouter
from fastapi.responses import JSONResponse
from models.schemas import ChatRequest
from core.state import app_state 

router = APIRouter()

@router.post("/context")
async def accept_context(request: ChatRequest):
    try:
        app_state.context = request.message
        response = "ok"
        return {"response": response}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})   
    