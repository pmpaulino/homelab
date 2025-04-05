# tests/test_main.py

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_read_item():
    item_id = 1
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json() == {"item_id": item_id, "q": None}


def test_update_item():
    item_id = 1
    item_data = {"name": "Test Item", "price": 10.0, "is_offer": True}
    response = client.put(f"/items/{item_id}", json=item_data)
    assert response.status_code == 200
    assert response.json() == {"item_name": "Test Item", "item_id": item_id}
