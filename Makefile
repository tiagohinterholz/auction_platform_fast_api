
dev:
	uv run uvicorn main:app --reload --port 8000

worker:
	uv run celery -A app.core.celery.celery_app worker --loglevel=info

migrate:
	uv run alembic upgrade head

format:
	uv run ruff check --fix

test:
	docker exec fastapi_auction_api uv run pytest -v
