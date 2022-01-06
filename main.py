"""
RESTful API and index.html for mclauncher.
"""

from firebase_admin import auth

from firebase import initialize_firebase, is_authorized_user
from mclauncher.app import create_app
from mclauncher.minecraft import MinecraftConnection, MinecraftProtocol
from mclauncher.compute_engine import get_instance


def connect_minecraft(address: str) -> MinecraftProtocol:
    return MinecraftConnection(address)


initialize_firebase()
app = create_app(
    verify_id_token=auth.verify_id_token,
    is_authorized_user=is_authorized_user(),
    connect_minecraft=connect_minecraft,
    get_instance=get_instance,
)
