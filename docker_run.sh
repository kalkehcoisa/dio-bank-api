cp .env.docker.example .env

# build e start
docker compose up --build

docker compose exec api alembic upgrade head
