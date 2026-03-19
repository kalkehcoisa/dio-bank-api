from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.auth import login_required
from src.database import get_db
from src.models import Account, Transaction, TransactionType, User
from src.schemas import StatementOut, TransactionCreate, TransactionOut

router = APIRouter(prefix="/transactions", tags=["Transações"])

LoginRequired = Annotated[User, Depends(login_required)]


async def _get_account(user: User, db: AsyncSession) -> Account:
    result = await db.execute(
        select(Account)
        .where(Account.user_id == user.id)
        .options(selectinload(Account.transactions))
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Conta não encontrada.")
    return account


@router.post(
    "/deposit",
    response_model=TransactionOut,
    status_code=status.HTTP_201_CREATED,
    summary="Realizar depósito",
    description="Adiciona um valor positivo ao saldo da conta corrente do usuário autenticado.",
)
async def deposit(
    payload: TransactionCreate,
    current_user: LoginRequired,
    db: AsyncSession = Depends(get_db),
):
    account = await _get_account(current_user, db)
    account.balance = Decimal(str(account.balance)) + payload.amount
    transaction = Transaction(
        account_id=account.id,
        type=TransactionType.deposit,
        amount=payload.amount,
        description=payload.description,
    )
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    return transaction


@router.post(
    "/withdraw",
    response_model=TransactionOut,
    status_code=status.HTTP_201_CREATED,
    summary="Realizar saque",
    description=(
        "Debita um valor da conta corrente do usuário autenticado. "
        "Rejeita se o saldo for insuficiente."
    ),
)
async def withdraw(
    payload: TransactionCreate,
    current_user: LoginRequired,
    db: AsyncSession = Depends(get_db),
):
    account = await _get_account(current_user, db)
    current_balance = Decimal(str(account.balance))
    if payload.amount > current_balance:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Saldo insuficiente. Saldo atual: R$ {current_balance:.2f}",
        )
    account.balance = current_balance - payload.amount
    transaction = Transaction(
        account_id=account.id,
        type=TransactionType.withdrawal,
        amount=payload.amount,
        description=payload.description,
    )
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    return transaction


@router.get(
    "/statement",
    response_model=StatementOut,
    summary="Extrato da conta",
    description=(
        "Retorna o saldo atual e o histórico completo de transações da conta,"
        " ordenado da mais recente para a mais antiga."
    ),
)
async def statement(
    current_user: LoginRequired,
    db: AsyncSession = Depends(get_db),
):
    account = await _get_account(current_user, db)
    return StatementOut(
        account_id=account.id,
        balance=account.balance,
        transactions=account.transactions,
    )
