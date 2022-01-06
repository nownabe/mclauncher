"""Sub app for api"""

from logging import getLogger

from typing import Callable
from fastapi import FastAPI
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
            logger.error(f'Error(get_instance): {type(error)=}: {error=}')
            return {"error": str(error)}

        if instance.is_running:
            try:
                connection = connect_minecraft(instance.address)
                status = MinecraftStatus(connection)
                await status.read_status()
                response.running = True
                response.players = status.players()
            except Exception as error:
                logger.warn(f'Error(minecraft): {type(error)=}: {error=}')

        return response

    @app.post("/server/start", response_model=schema.StartServerResponse)
    def start_server():
        """
        Start the server.
        """
        return {"ok": False}

    return app
