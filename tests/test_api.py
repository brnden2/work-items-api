import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

import main
from database import get_session


@pytest.fixture
def client(monkeypatch):
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(test_engine)

    def override_get_session():
        with Session(test_engine) as session:
            yield session

    monkeypatch.setattr(main, "create_db_and_tables", lambda: None)
    main.app.dependency_overrides[get_session] = override_get_session

    try:
        with TestClient(main.app) as test_client:
            yield test_client
    finally:
        main.app.dependency_overrides.pop(get_session, None)
        test_engine.dispose()

def test_get_work_items(client):
    response = client.get("/work-items")

    assert response.status_code == 200
    assert response.json() == []


def test_create_work_item_with_short_title(client):
    response = client.post(
        "/work-items",
        json={"title": "Hi", "status": "open"},
    )

    assert response.status_code == 422
    assert client.get("/work-items").json() == []


def test_create_work_item_with_invalid_status(client):
    response = client.post(
        "/work-items",
        json={"title": "Valid title", "status": "invalid"},
    )

    assert response.status_code == 422
    assert client.get("/work-items").json() == []


def test_get_work_item_not_found(client):
    response = client.get("/work-items/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Work item not found"

def test_create_and_retrieve_work_item(client):
    response = client.post(
        "/work-items",
        json={"title": "Prepare onboarding checklist", "status": "open"},
    )

    assert response.status_code == 201
    created = response.json()
    assert isinstance(created["id"], int)
    assert created["title"] == "Prepare onboarding checklist"
    assert created["status"] == "open"

    retrieved = client.get(f"/work-items/{created['id']}")
    assert retrieved.status_code == 200
    assert retrieved.json() == created

    listing = client.get("/work-items")
    assert listing.status_code == 200
    assert listing.json() == [created]

def test_update_work_item(client):
    created_response = client.post(
        "/work-items",
        json={"title": "Prepare checklist","status": "open"},
    )
    assert created_response.status_code == 201
    created = created_response.json()
    item_id = created["id"]

    response = client.patch(
        f"/work-items/{item_id}",
        json={"status": "in_progress"},
    )

    assert response.status_code == 200
    updated = response.json()
    assert updated["id"] == item_id
    assert updated["title"] == "Prepare checklist"
    assert updated["status"] == "in_progress"

    retrieved = client.get(f"/work-items/{item_id}")
    assert retrieved.status_code == 200
    assert retrieved.json() == updated

def test_delete_work_item(client):
    created_response = client.post(
        "/work-items",
        json={"title": "Temporary test task", "status": "open"},
    )
    assert created_response.status_code == 201
    item_id = created_response.json()["id"]

    deleted = client.delete(f"/work-items/{item_id}")
    assert deleted.status_code == 204
    assert deleted.content == b""

    retrieved = client.get(f"/work-items/{item_id}")
    assert retrieved.status_code == 404
    assert retrieved.json()["detail"] == "Work item not found"

    listing = client.get("/work-items")
    assert listing.status_code == 200
    assert listing.json() == []

@pytest.mark.parametrize(
    "invalid_update",
    [
        {"title": "Hi"},
        {"status": "invalid"},
    ],
)
def test_invalid_update_preserves_work_item(client, invalid_update):
    created_response = client.post(
        "/work-items",
        json={"title": "Keep original task", "status": "open"},
    )
    assert created_response.status_code == 201
    original = created_response.json()

    response = client.patch(
        f"/work-items/{original['id']}",
        json=invalid_update,
    )
    assert response.status_code == 422

    retrieved = client.get(f"/work-items/{original['id']}")
    assert retrieved.status_code == 200
    assert retrieved.json() == original

@pytest.mark.parametrize(
    "invalid_update",
    [
        {"title": None},
        {"status": None},
        {},
        {"title": "   "},
    ],
)
def test_reject_empty_or_null_updates(client, invalid_update):
    created_response = client.post(
        "/work-items",
        json={"title": "Preserve this task", "status": "open"},
    )
    assert created_response.status_code == 201
    original = created_response.json()

    # Capture server errors as responses so we can check stored data too.
    client.raise_server_exceptions = False

    response = client.patch(
        f"/work-items/{original['id']}",
        json=invalid_update,
    )

    retrieved = client.get(f"/work-items/{original['id']}")
    assert retrieved.status_code == 200
    assert retrieved.json() == original
    assert response.status_code == 422