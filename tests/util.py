import json
from typing import Callable

from mclauncher.minecraft import MinecraftProtocolBuffer, MinecraftStatus, MinecraftProtocol

def minecraft_connector(status: dict) -> Callable[[], MinecraftProtocol]:
    def _minecraft_connector() -> MinecraftProtocol:
        content_buffer = MinecraftProtocolBuffer()
        content_buffer.write_varint(0)
        content_buffer.write_string(json.dumps(status))
        response_buffer = MinecraftProtocolBuffer()
        response_buffer.write_varint(len(content_buffer))
        response_buffer.write(content_buffer.flush())

        return MinecraftProtocolBuffer(response_buffer.flush())

    return _minecraft_connector