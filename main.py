"""
RESTful API and index.html for mclauncher.
"""

from os import environ
from firebase_admin import auth

from firebase import count_consecutive_vacant, is_authorized_user, reset_consecutive_vacant
from mclauncher.app import create_app
from mclauncher.minecraft import MinecraftConnection, MinecraftProtocol
from mclauncher.compute_engine import get_instance, start_instance, stop_instance
from mclauncher.shutter import build_shutdown, build_shutter_authorize


def connect_minecraft(address: str) -> MinecraftProtocol:
    return MinecraftConnection(address)


shutter_authorize = build_shutter_authorize(
    authorized_email=environ['SHUTTER_EMAIL'],
)
shutdown = build_shutdown(
    connect_minecraft=connect_minecraft,
    get_instance=get_instance,
    stop_instance=stop_instance,
    count_consecutive_vacant=count_consecutive_vacant,
    reset_consecutive_vacant=reset_consecutive_vacant,
    shutdown_count=int(environ["SHUTTER_COUNT"])
)


app = create_app(
    title=environ["TITLE"],
    firebase_config_json=environ["FIREBASE_CONFIG_JSON"],
    verify_id_token=auth.verify_id_token,
    is_authorized_user=is_authorized_user,
    connect_minecraft=connect_minecraft,
    get_instance=get_instance,
    start_instance=start_instance,
    shutter_authorize=shutter_authorize,
    shutdown=shutdown,
)
