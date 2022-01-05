import json
import pytest

from mclauncher.minecraft import MinecraftProtocolBuffer, MinecraftStatus


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
    content_buffer = MinecraftProtocolBuffer()
    content_buffer.write_varint(0)
    content_buffer.write_string(json.dumps(status))
    response_buffer = MinecraftProtocolBuffer()
    response_buffer.write_varint(len(content_buffer))
    response_buffer.write(content_buffer.flush())

    mock = MinecraftProtocolBuffer(response_buffer.flush())

    status = MinecraftStatus(mock)
    await status.read_status()

    assert status.description() == 'A Minecraft Server'
    assert status.players() == ['Player 1', 'Player 2']
    assert status.version() == '1.18'
