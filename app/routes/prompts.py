
from fastapi import APIRouter
from services.agent import get_prompts

router = APIRouter()

@router.get("/prompts")
async def get_prompt_suggestions():
    return {"prompts": await get_prompts()}
