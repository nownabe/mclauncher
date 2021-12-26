"""
Define get_server to handle GET /api/v1/server.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from pydantic.fields import Field

router = APIRouter()


class GetServerResponse(BaseModel):
    """Response for /api/v1/server."""
    running: bool = Field(description="Wether the server is running or not.")
    players: list[str] = Field(
        description="A list of players joining the server.",
        example=["Steve", "Alex"]
        )


@router.get("/server", response_model=GetServerResponse)
async def get_server():
    """
    Returns the server status.
    """
    return GetServerResponse(False, [])
