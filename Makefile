.PHONY: run lint test migration generate_migration

run:
	alembic upgrade head
	uvicorn src.main:app --reload

lint:
	ruff format
	ruff check --fix

test:
	python3 -m pytest

generate_migration:
	@read -p "Enter migration name: " migration_name; \
	alembic revision --autogenerate -m "$${migration_name}"

migration:
	alembic upgrade head
