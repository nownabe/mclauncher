from typing import Callable

from google.auth.transport.requests import Request as AuthRequest
from google.oauth2.id_token import verify_token
from mclauncher.compute_engine import ComputeEngine
from mclauncher.config import Config
from mclauncher.firebase import Firebase

from mclauncher.minecraft import MinecraftProtocol, MinecraftStatus


_AUTH_SCHEME = "Bearer"


class Shutter:
    def __init__(
        self,
        config: Config,
        connect_minecraft: Callable[[str], MinecraftProtocol],
        firebase: Firebase,
        compute_engine: ComputeEngine
    ):
        self.authorized_email = config.shutter_authorized_email
        self.count_to_shutdown = config.shutter_count_to_shutdown
        self.connect_minecraft = connect_minecraft
        self.firebase = firebase
        self.compute_engine = compute_engine

    def shutter_authorize(self, authorization: str) -> bool:
        id_token = authorization[len(_AUTH_SCHEME)+1:]
        result = self._verify_token(id_token)
        return result["email"] == self.authorized_email

    async def shutdown(self):
        instance = self.compute_engine.get_instance()

        if not instance.is_running:
            self.firebase.reset_consecutive_vacant()
            return

        connection = self.connect_minecraft(instance.address)
        mc_status = MinecraftStatus(connection)
        await mc_status.read_status()

        if len(mc_status.players()) > 0:
            self.firebase.reset_consecutive_vacant()
            return

        count = self.firebase.count_consecutive_vacant()
        if count >= self.count_to_shutdown:
            self.compute_engine.stop_instance()
            self.firebase.reset_consecutive_vacant()

    def _verify_token(self, id_token: str):
        return verify_token(id_token, AuthRequest())
