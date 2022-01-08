"""
RESTful API and index.html for mclauncher.
"""

from mclauncher.app import create_app
from mclauncher.config import Config
from mclauncher.minecraft import MinecraftConnection, MinecraftProtocol


def connect_minecraft(address: str) -> MinecraftProtocol:
    return MinecraftConnection(address)


app = create_app(
    config=Config(),
    connect_minecraft=connect_minecraft,
)
