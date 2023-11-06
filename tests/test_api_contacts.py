import asyncio
from unittest.mock import MagicMock

import pytest

from src.database.models import User

contact = {
    "first_name": "Maksym",
    "last_name": "Klym",
    "phone": "+380936644885",
    "email": "test@example.com",
    "birthday": "1990-10-01",
}


@pytest.fixture
def token(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/v1/auth/signup", json=user)
    current_user: User = (
        session.query(User).filter(User.email == user["email"]).first()
    )
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "api/v1/auth/login",
        data={"username": user["email"], "password": user["password"]},
    )
    data = response.json()
    return data["access_token"]


def test_list_contacts_empty(client, token):
    response = client.get(
        "api/v1/contacts/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "There is no contacts"


def test_create_contact(client, token):
    response = client.post(
        "api/v1/contacts/",
        json=contact,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert "id" in data


def test_list_contacts(client, token):
    response = client.get(
        "api/v1/contacts/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert type(data) is list
    assert data[0]["first_name"] == contact["first_name"]
    assert data[0]["last_name"] == contact["last_name"]
    assert data[0]["email"] == contact["email"]


@pytest.mark.parametrize(
    "param, value",
    [
        ("first_name", contact["first_name"]),
        ("last_name", contact["last_name"]),
        ("email", contact["email"]),
    ],
)
def test_list_contacts_with_param(client, token, param, value):
    response = client.get(
        f"api/v1/contacts/?{param}={value}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data[param] == value


@pytest.mark.parametrize(
    "param, value",
    [
        ("first_name", "Wrong_first_name"),
        ("last_name", "Wrong_last_name"),
        ("email", "Wrong_email"),
    ],
)
def test_list_contacts_wrong_param(client, token, param, value):
    response = client.get(
        f"api/v1/contacts/?{param}={value}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "There is no contacts"
