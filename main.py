"""
RESTful API and index.html for mclauncher.
"""

from os import environ

from firebase_admin import auth

from firebase import initialize_firebase, is_authorized_user
from mclauncher.app import create_app
from mclauncher.minecraft import MinecraftConnection


def minecraft_connector():
    addr = environ['MINECRAFT_ADDRESS']
    return MinecraftConnection(addr)


initialize_firebase()
app = create_app(
    verify_id_token=auth.verify_id_token,
    is_authorized_user=is_authorized_user(),
    minecraft_connector=minecraft_connector,
)
