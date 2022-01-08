from typing import Awaitable, Callable

from google.auth.transport.requests import Request as AuthRequest
from google.oauth2.id_token import verify_token
from mclauncher.firebase import Firebase
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
    firebase: Firebase,
    shutdown_count: int,
) -> Callable[[], Awaitable[None]]:
    async def shutdown():
        instance = get_instance()

        if not instance.is_running:
            firebase.reset_consecutive_vacant()
            return

        connection = connect_minecraft(instance.address)
        mc_status = MinecraftStatus(connection)
        await mc_status.read_status()

        if len(mc_status.players()) > 0:
            firebase.reset_consecutive_vacant()
            return

        count = firebase.count_consecutive_vacant()
        if count >= shutdown_count:
            stop_instance()
            firebase.reset_consecutive_vacant()

    return shutdown
