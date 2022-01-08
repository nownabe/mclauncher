"""
RESTful API and index.html for mclauncher.
"""

import json
from os import environ

from mclauncher.app import create_app
from mclauncher.firebase import Firebase
from mclauncher.minecraft import MinecraftConnection, MinecraftProtocol
from mclauncher.compute_engine import get_instance, start_instance, stop_instance
from mclauncher.shutter import build_shutdown, build_shutter_authorize



firebase = Firebase(json.loads(environ['FIREBASE_CREDENTIALS_JSON']))


def connect_minecraft(address: str) -> MinecraftProtocol:
    return MinecraftConnection(address)


shutter_authorize = build_shutter_authorize(
    authorized_email=environ['SHUTTER_EMAIL'],
)
shutdown = build_shutdown(
    connect_minecraft=connect_minecraft,
    get_instance=get_instance,
    stop_instance=stop_instance,
    firebase=firebase,
    shutdown_count=int(environ["SHUTTER_COUNT"])
)


app = create_app(
    title=environ["TITLE"],
    firebase_config_json=environ["FIREBASE_CONFIG_JSON"],
    firebase=firebase,
    verify_id_token=firebase.verify_id_token,
    connect_minecraft=connect_minecraft,
    get_instance=get_instance,
    start_instance=start_instance,
    shutter_authorize=shutter_authorize,
    shutdown=shutdown,
)
