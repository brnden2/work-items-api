import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_get_work_items(client):
    response = client.get("/work-items")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_work_item_with_short_title(client):
    response = client.post(
        "/work-items",
        json={
            "title": "Hi",
            "status": "open"
        }
    )

    assert response.status_code == 422


def test_create_work_item_with_invalid_status(client):
    response = client.post(
        "/work-items",
        json={
            "title": "Valid title",
            "status": "invalid"
        }
    )

    assert response.status_code == 422


def test_get_work_item_not_found(client):
    response = client.get("/work-items/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Work item not found"