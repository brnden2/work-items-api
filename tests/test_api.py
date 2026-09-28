from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_get_work_items():
    response = client.get("/work-items")

    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_work_item_with_short_title():
    response = client.post(
        "/work-items",
        json={
            "title": "Hi",
            "status": "open"
        }
    )

    assert response.status_code == 422

def test_create_work_item_with_invalid_status():
    response = client.post(
        "/work-items",
        json={
            "title": "valid title",
            "status": "invalid"
        }
    )
    assert response.status_code == 422

def test_get_work_items_not_found():
    response = client.get("/work-items/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Work item not found"