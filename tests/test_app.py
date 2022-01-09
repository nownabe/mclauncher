"""Tests for main.py"""

from typing import Any
from fastapi.testclient import TestClient
from firebase_admin import initialize_app
from google.cloud import firestore

from mclauncher.app import create_app
from mclauncher.compute_engine import ComputeEngine
from mclauncher.config import Config
from mclauncher.firebase import Firebase
from mclauncher.instance import Instance
from mclauncher.minecraft import MinecraftProtocolBuffer

from .util import connect_minecraft


class MockConfig(Config):
    authorized_users: list[str] = ['authorized@example.com']
    shutter_authorized_email: str = 'shutter@example.com'
    instance_zone: str = 'asia-northeast1-a'
    instance_name: str = 'minecraft'
    is_running: bool = True


class MockFirebase(Firebase):
    def __init__(self, config: MockConfig):
        self.authorized_users = config.authorized_users
        self.counter = 0

    def count_consecutive_vacant(self) -> int:
        self.counter += 1
        return self.counter

    def reset_consecutive_vacant(self) -> None:
        self.counter = 0

    def verify_id_token(self, id_token: str) -> Any:
        return {'email': id_token}

    def _authorized_users(self) -> list[str]:
        return self.authorized_users


class MockComputeEngine(ComputeEngine):
    def __init__(self, config):
        self.config = config

    def get_instance(self) -> Instance:
        return Instance(is_running=self.config.is_running, address="dummy")

    def start_instance(self) -> bool:
        return True

    def stop_instance(self) -> bool:
        return True


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
    is_running=True,
):
    config = MockConfig(is_running=is_running)
    app = create_app(
        config=config,
        connect_minecraft=connect_minecraft,
        firebase_class=firebase_class,
        compute_engine_class=compute_engine_class,
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


def test_post_api_v1_server_server_not_ready():
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
