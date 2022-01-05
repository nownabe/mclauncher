"""Sub app for api"""

from typing import Callable
from fastapi import FastAPI

from mclauncher.minecraft import MinecraftProtocol, MinecraftStatus

from . import schema


def create_app(minecraft_connector: Callable[[], MinecraftProtocol]) -> FastAPI:
    app = FastAPI(root_path="/api/v1")


    @app.get("/server", response_model=schema.GetServerResponse)
    async def get_server():
        """
        Returns the server status.
        """
        response = schema.GetServerResponse(running=False, players=[])

        try:
            connection = minecraft_connector()
            status = MinecraftStatus(connection)
            await status.read_status()
            response.running = True
            response.players = status.players()
        except TimeoutError:
            pass

        return response


    @app.post("/server/start", response_model=schema.StartServerResponse)
    def start_server():
        """
        Start the server.
        """
        return {"ok": False}

    return app