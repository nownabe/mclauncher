"""Tests for main.py"""

from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)


def test_index():
    """Test for GET /"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "hello world"}
