import time
from typing import Annotated
from uuid import uuid4

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AccessToken(BaseModel):
    iss: str
    sub: str
    aud: str
    exp: float
    iat: float
    nbf: float
    jti: str


class JWTToken(BaseModel):
    access_token: AccessToken


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def sign_jwt(username: str) -> dict:
    s = get_settings()
    now = time.time()
    payload = {
        "iss": "bank-api",
        "sub": username,
        "aud": "bank-api-client",
        "exp": now + (s.access_token_expire_minutes * 60),
        "iat": now,
        "nbf": now,
        "jti": uuid4().hex,
    }
    token = jwt.encode(payload, s.secret_key, algorithm=s.algorithm)
    return {"access_token": token}


async def decode_jwt(token: str) -> JWTToken | None:
    s = get_settings()
    try:
        decoded = jwt.decode(
            token,
            s.secret_key,
            audience="bank-api-client",
            algorithms=[s.algorithm],
        )
        parsed = JWTToken.model_validate({"access_token": decoded})
        return parsed if parsed.access_token.exp >= time.time() else None
    except Exception:
        return None


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> JWTToken:
        authorization = request.headers.get("Authorization", "")
        scheme, _, credentials = authorization.partition(" ")
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header ausente ou inválido.",
            )
        if scheme != "Bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Esquema de autenticação inválido.",
            )
        payload = await decode_jwt(credentials)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido ou expirado.",
            )
        return payload


async def get_current_user(
    token: Annotated[JWTToken, Depends(JWTBearer())],
    db: AsyncSession = Depends(get_db),
):
    from src.models import User

    result = await db.execute(select(User).where(User.username == token.access_token.sub))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado.")
    return user


def login_required(
    current_user: Annotated[object, Depends(get_current_user)],
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado.")
    return current_user
