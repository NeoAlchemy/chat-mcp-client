from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/")
async def serve_index():
    with open("frontend/index.html", "r") as f:
        return HTMLResponse(content=f.read())
    