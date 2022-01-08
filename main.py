"""
RESTful API and index.html for mclauncher.
"""

from os import environ

from mclauncher.app import create_app
from mclauncher.config import Config
from mclauncher.minecraft import MinecraftConnection, MinecraftProtocol
from mclauncher.compute_engine import get_instance, start_instance, stop_instance


def connect_minecraft(address: str) -> MinecraftProtocol:
    return MinecraftConnection(address)


app = create_app(
    config=Config(),
    connect_minecraft=connect_minecraft,
    get_instance=get_instance,
    start_instance=start_instance,
    stop_instance=stop_instance,
)
