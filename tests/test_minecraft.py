import json
import pytest

from mclauncher.minecraft import MinecraftProtocolBuffer, MinecraftStatus

from .util import minecraft_connector

@pytest.mark.anyio
async def test_read_status():
    status = {
        'description': {
            'text': 'A Minecraft Server',
        },
        'players': {
            'sample': [
                {'name': 'Player 1'},
                {'name': 'Player 2'},
            ],
        },
        'version': {
            'name': '1.18'
        }
    }

    mock = minecraft_connector(status)()

    status = MinecraftStatus(mock)
    await status.read_status()

    assert status.description() == 'A Minecraft Server'
    assert status.players() == ['Player 1', 'Player 2']
    assert status.version() == '1.18'
