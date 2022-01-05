'''Classes to communicate Minecraft server'''

from abc import ABCMeta, abstractmethod
from asyncio.streams import StreamReader, StreamWriter
from ctypes import c_uint32 as uint32
from ctypes import c_int32 as int32
import asyncio
import json
import struct


class TooLongVarInt(Exception):
    pass


class AbstractMinecraftConnection(metaclass=ABCMeta):
    @abstractmethod
    async def connect(self):
        ...

    @abstractmethod
    async def read_status(self):
        ...


class MinecraftProtocol(metaclass=ABCMeta):
    @abstractmethod
    async def read(self, length: int) -> bytes:
        '''Read bytes'''
        ...

    @abstractmethod
    def write(self, data: bytes):
        '''Write bytes'''
        ...

    async def read_byte(self) -> int:
        '''Read a byte'''
        return (await self.read(1))[0]

    def write_byte(self, data: int):
        """Write a byte"""
        # Write 7 bits as unsigned char in network (big) endian
        self.write(struct.pack(">B", data))

    def write_ushort(self, data: int):
        """Write an unsigned short (2 bytes)."""
        self.write(struct.pack(">H", data))

    async def read_varint(self) -> int:
        '''Read a var int.'''
        data = 0
        for i in range(5):
            byte = await self.read_byte()
            data |= (byte & 0x7F) << 7 * i
            if byte & 0x80 != 0x80:
                return int32(data).value
        raise TooLongVarInt()

    def write_varint(self, data: int):
        """Write a var int"""
        data = uint32(data).value
        for _ in range(5):
            if data & ~0x7f == 0:
                self.write_byte(data)
                return

            self.write_byte(data & 0x7F | 0x80)
            data >>= 7

    async def read_string(self) -> str:
        '''Read a string.'''
        length = await self.read_varint()
        return (await self.read(length)).decode("utf8")

    def write_string(self, data: str):
        """Write a string"""
        self.write_varint(len(data))
        self.write(data.encode("utf8"))


class MinecraftProtocolBuffer(MinecraftProtocol):
    def __init__(self, data: bytes = b''):
        self.__read_buffer = bytearray(data)
        self.__write_buffer = bytearray()

    async def read(self, length: int) -> bytes:
        data = bytes(self.__read_buffer[:length])
        self.__read_buffer = self.__read_buffer[length:]
        return data

    def write(self, data: bytes):
        """Write bytes"""
        self.__write_buffer.extend(data)

    def flush(self) -> bytes:
        """Return buffered data and its flush buffer."""
        data = bytes(self.__write_buffer)
        self.__write_buffer = bytearray()
        return data


class MinecraftConnection(AbstractMinecraftConnection, MinecraftProtocol):
    '''
    TCP Connection to Minecraft server

    See also https://wiki.vg/Protocol
    '''

    __VERSION: int = 757  # Minecraft 1.18.1

    __reader: StreamReader
    __writer: StreamWriter

    def __init__(self, address, timeout=3):
        self.__host, *port = address.split(":")

        if len(port) == 0:
            self.__port = 25565
        else:
            self.__port = int(port[0])

        self.timeout = timeout
        self.__connected = False

    async def connect(self):
        '''Connect to the server and do the handshake'''
        if self.__connected:
            return

        conn = asyncio.open_connection(self.__host, self.__port)
        self.__reader, self.__writer = await asyncio.wait_for(conn, timeout=self.timeout)
        await self.__handshake()
        self.__connected = True

    async def read_status(self) -> dict:
        buffer = MinecraftProtocolBuffer()
        buffer.write_varint(0)
        self.__write_buffer(buffer)

        length = await self.read_varint()
        result = MinecraftProtocolBuffer(await self.read(length))

        if await result.read_varint() != 0:
            raise IOError("invalid response")

        return json.loads(await result.read_string())

    async def read(self, length: int) -> bytes:
        data = bytearray()
        while len(data) < length:
            val = await asyncio.wait_for(
                self.__reader.read(length - len(data)),
                timeout=self.timeout
            )
            if len(val) == 0:
                raise IOError('got no data from server')
            data.extend(val)
        return bytes(data)

    def write(self, data: bytes):
        '''Write data to the connected server.'''
        self.__writer.write(data)

    async def __handshake(self):
        buffer = MinecraftProtocolBuffer()
        buffer.write_varint(0)
        buffer.write_varint(self.__VERSION)
        buffer.write_string(self.__host)
        buffer.write_ushort(self.__port)
        buffer.write_varint(1)

        self.__write_buffer(buffer)

    def __write_buffer(self, buffer: MinecraftProtocolBuffer):
        data = buffer.flush()
        self.write_varint(len(data))
        self.write(data)

    def __del__(self):
        try:
            self.__writer.close()
        except:
            pass


class MinecraftStatus:
    '''Minecraft server status'''

    __status: dict = None

    def __init__(self, connection: AbstractMinecraftConnection):
        self.__connection = connection

    async def read_status(self):
        if self.__status is not None:
            return

        await self.__connection.connect()
        self.__status = await self.__connection.read_status()

    def description(self) -> str:
        return self.__status['description']['text']

    def players(self) -> list[str]:
        _players = self.__status['players']

        if 'sample' not in _players:
            return []

        return [player['name'] for player in _players['sample']]

    def version(self) -> str:
        return self.__status['version']['name']
