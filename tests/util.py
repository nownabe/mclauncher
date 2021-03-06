import json
from typing import Callable

from mclauncher.minecraft import MinecraftProtocolBuffer, MinecraftProtocol


def connect_minecraft(
    status: dict,
    protocol_class: type[MinecraftProtocolBuffer] = MinecraftProtocolBuffer,
) -> Callable[[str], MinecraftProtocol]:
    def _minecraft_connector(_: str) -> MinecraftProtocol:
        content_buffer = MinecraftProtocolBuffer()
        content_buffer.write_varint(0)
        content_buffer.write_string(json.dumps(status))
        response_buffer = MinecraftProtocolBuffer()
        response_buffer.write_varint(len(content_buffer))
        response_buffer.write(content_buffer.flush())

        return protocol_class(response_buffer.flush())

    return _minecraft_connector
