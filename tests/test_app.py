"""Tests for main.py"""

from typing import Callable
from fastapi.testclient import TestClient

from mclauncher.app import create_app
from mclauncher.instance import Instance
from mclauncher.minecraft import MinecraftProtocolBuffer

from .util import connect_minecraft


def verify_id_token(email: str):
    return {'email': email}


def is_authorized_user(email: str):
    return email == 'authorized'


def get_instance(is_running: bool = True) -> Callable[[], Instance]:
    def _get_instance() -> Instance:
        return Instance(is_running=is_running, address="dummy")

    return _get_instance


def start_instance():
    pass


def shutter_authorize(email: str):
    return True


async def shutdown():
    pass


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
    verify_id_token=verify_id_token,
    is_authorized_user=is_authorized_user,
    connect_minecraft=connect_minecraft(status),
    get_instance=get_instance(),
    start_instance=start_instance,
    shutter_authorize=shutter_authorize,
    shutdown=shutdown,
):
    app = create_app(
        title="mclauncher",
        firebase_config_json='{}',
        verify_id_token=verify_id_token,
        is_authorized_user=is_authorized_user,
        connect_minecraft=connect_minecraft,
        get_instance=get_instance,
        start_instance=start_instance,
        shutter_authorize=shutter_authorize,
        shutdown=shutdown,
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
        headers={'Authorization': 'Bearer authorized'}
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
    client = create_client(get_instance=get_instance(False))
    response = client.get(
        '/api/v1/server',
        headers={'Authorization': 'Bearer authorized'}
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
        headers={'Authorization': 'Bearer authorized'}
    )
    assert response.status_code == 500


def test_post_api_v1_server_start_authorized():
    response = client.post(
        '/api/v1/server/start',
        headers={'Authorization': 'Bearer authorized'}
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
    client = create_client(get_instance=get_instance(False))
    response = client.post(
        '/api/v1/server/start',
        headers={'Authorization': 'Bearer authorized'}
    )
    assert response.status_code == 200
    assert response.json() == {'ok': True}
