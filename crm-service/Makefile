.PHONY: help install run test clean docker-build docker-up docker-down migrate

help:
	@echo "Comandos disponibles:"
	@echo "  make install       - Instalar dependencias"
	@echo "  make run          - Ejecutar aplicación en desarrollo"
	@echo "  make test         - Ejecutar tests"
	@echo "  make clean        - Limpiar archivos temporales"
	@echo "  make docker-build - Construir imagen Docker"
	@echo "  make docker-up    - Levantar servicios con Docker Compose"
	@echo "  make docker-down  - Detener servicios Docker"
	@echo "  make migrate      - Ejecutar migraciones de base de datos"

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

run:
	python run.py

test:
	pytest -v

test-coverage:
	pytest --cov=app --cov-report=html

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f crm-service

migrate:
	flask db upgrade

migrate-create:
	flask db migrate -m "$(message)"

lint:
	flake8 app/ --max-line-length=100

format:
	black app/
