import pytest

from mclauncher.minecraft import MinecraftStatus

from .util import connect_minecraft


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

    mock = connect_minecraft(status)("dummy")

    status = MinecraftStatus(mock)
    await status.read_status()

    assert status.description() == 'A Minecraft Server'
    assert status.players() == ['Player 1', 'Player 2']
    assert status.version() == '1.18'
