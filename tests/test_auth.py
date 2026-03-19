import pytest
from httpx import AsyncClient


async def test_register(client: AsyncClient):
    r = await client.post(
        "/users/register", json={"username": "joao", "password": "123456"}
    )
    assert r.status_code == 201
    data = r.json()
    assert data["username"] == "joao"
    assert "id" in data


async def test_register_duplicate(client: AsyncClient):
    await client.post(
        "/users/register", json={"username": "joao", "password": "123456"}
    )
    r = await client.post(
        "/users/register", json={"username": "joao", "password": "outrasenha"}
    )
    assert r.status_code == 400


async def test_register_short_password(client: AsyncClient):
    r = await client.post(
        "/users/register", json={"username": "joao", "password": "123"}
    )
    assert r.status_code == 422


async def test_login(client: AsyncClient):
    await client.post(
        "/users/register", json={"username": "joao", "password": "123456"}
    )
    r = await client.post(
        "/users/token", data={"username": "joao", "password": "123456"}
    )
    assert r.status_code == 200
    assert "access_token" in r.json()


async def test_login_wrong_password(client: AsyncClient):
    await client.post(
        "/users/register", json={"username": "joao", "password": "123456"}
    )
    r = await client.post(
        "/users/token", data={"username": "joao", "password": "errada"}
    )
    assert r.status_code == 401


async def test_me(auth_client: AsyncClient):
    r = await auth_client.get("/users/me")
    assert r.status_code == 200
    assert r.json()["username"] == "testuser"


async def test_me_no_token(client: AsyncClient):
    r = await client.get("/users/me")
    assert r.status_code == 401
