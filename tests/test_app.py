"""Tests for main.py"""

from typing import Any, ClassVar

from fastapi.testclient import TestClient

from mclauncher.app import create_app
from mclauncher.compute_engine import ComputeEngine
from mclauncher.config import Config
from mclauncher.firebase import Firebase
from mclauncher.instance import Instance
from mclauncher.minecraft import MinecraftProtocolBuffer
from mclauncher.shutter import Shutter

from .util import connect_minecraft


class MockConfig(Config):
    authorized_users: list[str] = ['authorized@example.com']
    shutter_authorized_email: str = 'shutter@example.com'
    instance_zone: str = 'asia-northeast1-a'
    instance_name: str = 'minecraft'
    is_running: bool = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shutter_authorized_email = 'shutter@example.com'


class MockFirebase(Firebase):
    counter: ClassVar[int]

    def __init__(self, config: MockConfig):
        self.authorized_users = config.authorized_users
        MockFirebase.counter = 0

    def count_consecutive_vacant(self) -> int:
        MockFirebase.counter += 1
        return MockFirebase.counter

    def reset_consecutive_vacant(self) -> None:
        MockFirebase.counter = 0

    def verify_id_token(self, id_token: str) -> Any:
        return {'email': id_token}

    def _authorized_users(self) -> list[str]:
        return self.authorized_users


class MockComputeEngine(ComputeEngine):
    is_running: ClassVar[bool]

    def __init__(self, config):
        self.config = config
        MockComputeEngine.is_running = config.is_running

    def get_instance(self) -> Instance:
        return Instance(is_running=self._is_running(), address="dummy")

    def start_instance(self) -> bool:
        MockComputeEngine.is_running = True
        return True

    def stop_instance(self) -> bool:
        MockComputeEngine.is_running = False
        return True

    def _is_running(self) -> bool:
        return MockComputeEngine.is_running


class MockShutter(Shutter):
    def _verify_token(self, id_token: str):
        return {'email': id_token}


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


def create_client(
    connect_minecraft=connect_minecraft(status),
    firebase_class=MockFirebase,
    compute_engine_class=MockComputeEngine,
    shutter_class=MockShutter,
    is_running=True,
):
    config = MockConfig(is_running=is_running)
    app = create_app(
        config=config,
        connect_minecraft=connect_minecraft,
        firebase_class=firebase_class,
        compute_engine_class=compute_engine_class,
        shutter_class=shutter_class,
    )
    return TestClient(app)


client = create_client()


def test_index():
    """Test for GET /"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers['content-type'] == 'text/html; charset=utf-8'


def test_get_api_v1_server_authorized():
    response = client.get(
        '/api/v1/server',
        headers={'Authorization': 'Bearer authorized@example.com'}
    )
    assert response.status_code == 200
    assert response.json() == {'running': True, 'players': [
        'Player 1', 'Player 2']}


def test_get_api_v1_server_unauthorized():
    response = client.get(
        '/api/v1/server',
        headers={'Authorization': 'Bearer unauthorized'}
    )
    assert response.status_code == 403
    assert response.json() == {'detail': 'forbidden'}


def test_post_api_v1_server_instance_not_running():
    client = create_client(is_running=False)
    response = client.get(
        '/api/v1/server',
        headers={'Authorization': 'Bearer authorized@example.com'}
    )
    assert response.status_code == 200
    assert response.json() == {'running': False, 'players': []}


def test_post_api_v1_server_server_timeout():
    class NotRunningConnection(MinecraftProtocolBuffer):
        async def connect(self):
            raise TimeoutError()

    client = create_client(
        connect_minecraft=connect_minecraft(
            status, protocol_class=NotRunningConnection)
    )
    response = client.get(
        '/api/v1/server',
        headers={'Authorization': 'Bearer authorized@example.com'}
    )
    assert response.status_code == 500


def test_post_api_v1_server_server_connection_refused():
    class NotRunningConnection(MinecraftProtocolBuffer):
        async def connect(self):
            raise ConnectionRefusedError()

    client = create_client(
        connect_minecraft=connect_minecraft(
            status, protocol_class=NotRunningConnection)
    )
    response = client.get(
        '/api/v1/server',
        headers={'Authorization': 'Bearer authorized@example.com'}
    )
    assert response.status_code == 200
    assert response.json() == {'running': False, 'players': []}


def test_post_api_v1_server_start_authorized():
    response = client.post(
        '/api/v1/server/start',
        headers={'Authorization': 'Bearer authorized@example.com'}
    )
    assert response.status_code == 200
    assert response.json() == {'ok': False}


def test_post_api_v1_server_start_unauthorized():
    response = client.post(
        '/api/v1/server/start',
        headers={'Authorization': 'Bearer unauthorized'}
    )
    assert response.status_code == 403
    assert response.json() == {'detail': 'forbidden'}


def test_post_api_v1_server_start_success():
    client = create_client(is_running=False)
    response = client.post(
        '/api/v1/server/start',
        headers={'Authorization': 'Bearer authorized@example.com'}
    )
    assert response.status_code == 200
    assert response.json() == {'ok': True}


def test_post_shutter_unauthorized():
    response = client.post(
        '/shutter',
        headers={'Authorization': 'Bearer unauthorized'}
    )
    assert response.status_code == 403
    assert response.json() == {'detail': 'forbidden'}


def test_post_shutter_shutdown():
    client = create_client(
        connect_minecraft=connect_minecraft({
            'description': {'text': 'A Minecraft Server'},
            'players': {'sample': []},
            'version': {'name': '1.18'}
        })
    )
    response = client.post(
        '/shutter',
        headers={'Authorization': 'Bearer shutter@example.com'}
    )
    assert response.status_code == 200
    assert response.json() == {'ok': True}
    assert MockComputeEngine.is_running

    response = client.post(
        '/shutter',
        headers={'Authorization': 'Bearer shutter@example.com'}
    )
    assert response.status_code == 200
    assert response.json() == {'ok': True}
    assert not MockComputeEngine.is_running


def test_post_shutter_reset():
    client_without_players = create_client(
        connect_minecraft=connect_minecraft({
            'description': {'text': 'A Minecraft Server'},
            'players': {'sample': []},
            'version': {'name': '1.18'}
        })
    )
    response = client_without_players.post(
        '/shutter',
        headers={'Authorization': 'Bearer shutter@example.com'}
    )
    assert response.status_code == 200
    assert response.json() == {'ok': True}
    assert MockComputeEngine.is_running
    assert MockFirebase.counter == 1

    response = client.post(
        '/shutter',
        headers={'Authorization': 'Bearer shutter@example.com'}
    )
    assert response.status_code == 200
    assert response.json() == {'ok': True}
    assert MockComputeEngine.is_running
    assert MockFirebase.counter == 0
