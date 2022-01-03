"""API schemas"""

from pydantic import BaseModel
from pydantic.fields import Field


class GetServerResponse(BaseModel):
    """Response for /api/v1/server."""
    running: bool = Field(description="Wether the server is running or not.")
    players: list[str] = Field(
        description="A list of players joining the server.",
        example=["Steve", "Alex"]
    )


class StartServerResponse(BaseModel):
    """Response for /api/v1/server/start."""
    ok: bool
