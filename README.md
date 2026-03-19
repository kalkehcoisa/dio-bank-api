# API Bancária Assíncrona

API RESTful assíncrona com FastAPI, SQLAlchemy async, JWT e SQLite.

## Endpoints

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| POST | `/auth/register` | ❌ | Cadastrar usuário |
| POST | `/auth/token` | ❌ | Login (retorna JWT) |
| GET | `/auth/me` | ✅ | Dados do usuário logado |
| POST | `/transactions/deposit` | ✅ | Depósito |
| POST | `/transactions/withdraw` | ✅ | Saque |
| GET | `/transactions/statement` | ✅ | Extrato |

Documentação interativa disponível em `http://localhost:8000/docs`.

---

## Opção 1 — Poetry (local, sem container)

```bash
# instalar dependências
poetry install

# copiar e ajustar variáveis de ambiente
cp .env.example .env

# rodar migrações
poetry run alembic upgrade head

# iniciar servidor
poetry run uvicorn src.main:app --reload
```

### Testes

```bash
poetry run pytest tests/ -v
```

---

## Opção 2 — Docker

```bash
# copiar env para docker
cp .env.docker.example .env

# build e start
docker compose up --build
```

O banco fica persistido no volume `db_data`.  
Para aplicar migrações dentro do container:

```bash
docker compose exec api alembic upgrade head
```

---

## Variáveis de ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./bank.db` | URL do banco |
| `SECRET_KEY` | *(obrigatório em prod)* | Chave para assinar JWT |
| `ALGORITHM` | `HS256` | Algoritmo JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Expiração do token |

---

## Estrutura

```
bank_api/
├── src/
│   ├── config.py        # Settings (pydantic-settings)
│   ├── database.py      # Engine async + get_db
│   ├── models.py        # User, Account, Transaction
│   ├── schemas.py       # Pydantic I/O
│   ├── auth.py          # JWT + hash + get_current_user
│   ├── main.py          # App + lifespan
│   └── routers/
│       ├── auth.py
│       └── transactions.py
├── migrations/          # Alembic
├── tests/
│   ├── conftest.py      # Fixtures (DB in-memory, client, auth_client)
│   ├── test_auth.py
│   └── test_transactions.py
├── .env.example
├── .env.docker.example
├── pyproject.toml
├── Dockerfile
└── docker-compose.yml
```
