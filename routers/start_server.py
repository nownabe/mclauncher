"""
Define start_server to handle GET /api/v1/server/start.
"""

from fastapi import APIRouter
from pydantic.main import BaseModel

router = APIRouter()


class StartServerResponse(BaseModel):
    """Response for /api/v1/server/start."""
    ok: bool


@router.post("/server/start", response_model=StartServerResponse)
def start_server():
    """
    Start the server.
    """
    return {"ok": False}
