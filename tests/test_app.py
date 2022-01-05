"""Tests for main.py"""

from fastapi.testclient import TestClient

from mclauncher.app import create_app


def verify_id_token(email: str):
    return {'email': email}


def is_authorized_user(email: str):
    return email == 'authorized'


app = create_app(
    verify_id_token=verify_id_token,
    is_authorized_user=is_authorized_user
)

client = TestClient(app)


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
    assert response.json() == {'running': False, 'players': []}


def test_get_api_v1_server_unauthorized():
    response = client.get(
        '/api/v1/server',
        headers={'Authorization': 'Bearer unauthorized'}
    )
    assert response.status_code == 403
    assert response.json() == {'error': 'forbidden'}


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
    assert response.json() == {'error': 'forbidden'}
