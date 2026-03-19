from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import get_current_user, hash_password, sign_jwt, verify_password
from src.database import get_db
from src.models import Account, User
from src.schemas import Token, UserCreate, UserOut

router = APIRouter(prefix="/users", tags=["Autenticação"])

CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar novo usuário",
    description="Cria um novo usuário e inicializa sua conta corrente com saldo zero.",
)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == payload.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Nome de usuário já cadastrado.")

    user = User(
        username=payload.username, hashed_password=hash_password(payload.password)
    )
    db.add(user)
    await db.flush()

    account = Account(user_id=user.id)
    db.add(account)
    await db.commit()
    await db.refresh(user)
    return user


@router.post(
    "/token",
    response_model=Token,
    summary="Obter token JWT",
    description="Autentica o usuário e retorna um token de acesso Bearer.",
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return sign_jwt(user.username)


@router.get(
    "/me",
    response_model=UserOut,
    summary="Dados do usuário autenticado",
)
async def me(current_user: CurrentUser):
    return current_user
