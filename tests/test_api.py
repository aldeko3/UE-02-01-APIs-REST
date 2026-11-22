from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_healthcheck():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"message": "Hola Mundo!"}

def test_create_user_invalid_email():
    payload = {
        "username": "asier_dev",
        "first_name": "Asier",
        "first_surname": "Aldekoa",
        "email": "correo-no-valido",
    }
    response = client.post("/users", json=payload)
    assert response.status_code == 422


def test_create_user_invalid_username():
    payload = {
        "username": "ab",  # Menos de 3 caracteres
        "first_name": "Asier",
        "first_surname": "Aldekoa",
        "email": "asier@example.com",
    }
    response = client.post("/users", json=payload)
    assert response.status_code == 422