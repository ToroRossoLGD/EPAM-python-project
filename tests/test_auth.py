import pytest


@pytest.mark.asyncio
async def test_register_user(client):
    response = await client.post(
        "/auth",
        json={
            "login": "testuser",
            "password": "password123",
            "repeat_password": "password123",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["login"] == "testuser"
    assert "id" in data


@pytest.mark.asyncio
async def test_login_user(client):
    register_response = await client.post(
        "/auth",
        json={
            "login": "testlogin",
            "password": "password123",
            "repeat_password": "password123",
        },
    )
    assert register_response.status_code == 201

    login_response = await client.post(
        "/login",
        json={
            "login": "testlogin",
            "password": "password123",
        },
    )

    assert login_response.status_code == 200
    data = login_response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"