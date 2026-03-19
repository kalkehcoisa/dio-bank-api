from decimal import Decimal

from httpx import AsyncClient


async def test_deposit(auth_client: AsyncClient):
    r = await auth_client.post("/transactions/deposit", json={"amount": "200.00", "description": "pix"})
    assert r.status_code == 201
    data = r.json()
    assert data["type"] == "deposit"
    assert Decimal(data["amount"]) == Decimal("200.00")


async def test_deposit_negative(auth_client: AsyncClient):
    r = await auth_client.post("/transactions/deposit", json={"amount": "-50.00"})
    assert r.status_code == 422


async def test_deposit_zero(auth_client: AsyncClient):
    r = await auth_client.post("/transactions/deposit", json={"amount": "0"})
    assert r.status_code == 422


async def test_withdraw(auth_client: AsyncClient):
    await auth_client.post("/transactions/deposit", json={"amount": "500.00"})
    r = await auth_client.post("/transactions/withdraw", json={"amount": "100.00"})
    assert r.status_code == 201
    data = r.json()
    assert data["type"] == "withdrawal"
    assert Decimal(data["amount"]) == Decimal("100.00")


async def test_withdraw_insufficient_balance(auth_client: AsyncClient):
    await auth_client.post("/transactions/deposit", json={"amount": "100.00"})
    r = await auth_client.post("/transactions/withdraw", json={"amount": "9999.00"})
    assert r.status_code == 422
    assert "Saldo insuficiente" in r.json()["detail"]


async def test_withdraw_exact_balance(auth_client: AsyncClient):
    await auth_client.post("/transactions/deposit", json={"amount": "300.00"})
    r = await auth_client.post("/transactions/withdraw", json={"amount": "300.00"})
    assert r.status_code == 201


async def test_statement(auth_client: AsyncClient):
    await auth_client.post("/transactions/deposit", json={"amount": "400.00", "description": "salario"})
    await auth_client.post("/transactions/withdraw", json={"amount": "50.00", "description": "lanche"})
    r = await auth_client.get("/transactions/statement")
    assert r.status_code == 200
    data = r.json()
    assert Decimal(data["balance"]) == Decimal("350.00")
    assert len(data["transactions"]) == 2


async def test_statement_unauthenticated(client: AsyncClient):
    r = await client.get("/transactions/statement")
    assert r.status_code == 401


async def test_statement_empty(auth_client: AsyncClient):
    r = await auth_client.get("/transactions/statement")
    assert r.status_code == 200
    data = r.json()
    assert Decimal(data["balance"]) == Decimal("0.00")
    assert data["transactions"] == []
