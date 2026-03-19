cp .env.example .env

poetry run alembic upgrade head

# iniciar servidor
poetry run uvicorn src.main:app --reload
