"""Sub app for api"""

from logging import getLogger

from typing import Callable
from fastapi import FastAPI, status, HTTPException
from mclauncher.instance import Instance

from mclauncher.minecraft import MinecraftProtocol, MinecraftStatus

from . import schema


logger = getLogger('uvicorn')


def create_app(
    connect_minecraft: Callable[[str], MinecraftProtocol],
    get_instance: Callable[[], Instance],
) -> FastAPI:
    app = FastAPI(root_path="/api/v1")

    @app.get("/server", response_model=schema.GetServerResponse)
    async def get_server():
        """
        Returns the server status.
        """

        response = schema.GetServerResponse(running=False, players=[])

        try:
            instance = get_instance()
        except Exception as error:
            logger.error('get_instance(): %r', error)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(error)
            ) from error

        if not instance.is_running:
            return response

        try:
            connection = connect_minecraft(instance.address)
            mc_status = MinecraftStatus(connection)
            await mc_status.read_status()
            response.running = True
            response.players = mc_status.players()
        except Exception as error:
            logger.error('getting minecraft status: %r', error)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(error)
            ) from error

        return response

    @app.post("/server/start", response_model=schema.StartServerResponse)
    def start_server():
        """
        Start the server.
        """
        return {"ok": False}

    return app
