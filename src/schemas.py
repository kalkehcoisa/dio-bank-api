from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from src.models import TransactionType


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Nome de usuário único")
    password: str = Field(..., min_length=6, description="Senha com no mínimo 6 caracteres")


class UserOut(BaseModel):
    id: int
    username: str
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str | None = None


class AccountOut(BaseModel):
    id: int
    balance: Decimal
    created_at: datetime

    model_config = {"from_attributes": True}


class TransactionCreate(BaseModel):
    amount: Decimal = Field(..., gt=0, description="Valor da transação (deve ser positivo)")
    description: str | None = Field(None, max_length=255, description="Descrição opcional")

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("O valor deve ser maior que zero")
        return round(v, 2)


class TransactionOut(BaseModel):
    id: int
    type: TransactionType
    amount: Decimal
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class StatementOut(BaseModel):
    account_id: int
    balance: Decimal
    transactions: list[TransactionOut]
