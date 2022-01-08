"""Sub app for api"""

from logging import getLogger

from typing import Callable
from fastapi import FastAPI, status, HTTPException

from mclauncher.compute_engine import ComputeEngine
from mclauncher.minecraft import MinecraftProtocol, MinecraftStatus

from . import schema


logger = getLogger('uvicorn')


def create_app(
    connect_minecraft: Callable[[str], MinecraftProtocol],
    compute_engine: ComputeEngine,
) -> FastAPI:
    app = FastAPI(root_path="/api/v1")

    def _get_instance():
        try:
            return compute_engine.get_instance()
        except Exception as error:
            logger.error('get_instance(): %r', error)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(error)
            ) from error

    @app.get("/server", response_model=schema.GetServerResponse)
    async def get_server():
        """
        Returns the server status.
        """

        response = schema.GetServerResponse(running=False, players=[])

        instance = _get_instance()

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

        instance = _get_instance()

        if instance.is_running:
            return schema.StartServerResponse(ok=False)

        try:
            compute_engine.start_instance()
            return schema.StartServerResponse(ok=True)
        except Exception as error:
            logger.error('start_instance(): %r', error)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(error),
            ) from error

    return app
