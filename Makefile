.PHONY: dev test lint docker-up docker-down install clean

# Development
dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Testing
test:
	pytest --cov=app --cov-report=html --cov-report=term-missing

test-watch:
	pytest --cov=app --cov-report=term-missing -f

# Linting & Formatting
lint:
	ruff check app/ tests/
	black --check app/ tests/
	mypy app/

format:
	black app/ tests/
	ruff --fix app/ tests/

# Docker
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-build:
	docker-compose build

# Dependencies
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

# Database
migrate:
	alembic upgrade head

migrate-create:
	alembic revision --autogenerate -m "$(name)"

# Clean
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .coverage htmlcov/ .pytest_cache/ 