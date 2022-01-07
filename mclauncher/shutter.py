from typing import Awaitable, Callable

from google.auth.transport.requests import Request as AuthRequest
from google.oauth2.id_token import verify_token
from mclauncher.instance import Instance

from mclauncher.minecraft import MinecraftProtocol, MinecraftStatus


_AUTH_SCHEME = "Bearer"


def build_shutter_authorize(authorized_email: str):
    def shutter_authorize(authorization: str) -> bool:
        id_token = authorization[len(_AUTH_SCHEME)+1:]
        result = verify_token(id_token, AuthRequest())
        return result["email"] == authorized_email

    return shutter_authorize


def build_shutdown(
    connect_minecraft: Callable[[str], MinecraftProtocol],
    get_instance: Callable[[], Instance],
    stop_instance: Callable[[], bool],
    count_consecutive_vacant: Callable[[], int],
    reset_consecutive_vacant: Callable[[], None],
    shutdown_count: int,
) -> Callable[[], Awaitable[None]]:
    async def shutdown():
        instance = get_instance()

        if not instance.is_running:
            reset_consecutive_vacant()
            return

        connection = connect_minecraft(instance.address)
        mc_status = MinecraftStatus(connection)
        await mc_status.read_status()

        if len(mc_status.players()) > 0:
            reset_consecutive_vacant()
            return

        count = count_consecutive_vacant()
        if count >= shutdown_count:
            stop_instance()
            reset_consecutive_vacant()

    return shutdown