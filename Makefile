.PHONY: help env up down download ingest dbt-deps dbt-build dbt-test pipeline test validate logs

help:
	@echo "Targets:"
	@echo "  make env        Copy .env.example -> .env if missing"
	@echo "  make download   Download Olist CSVs into data/raw/"
	@echo "  make up         Build and start Postgres, Airflow, Metabase"
	@echo "  make down       Stop containers"
	@echo "  make pipeline   Hint: trigger the Airflow DAG after make up"
	@echo "  make test       Run Python unit tests"
	@echo "  make validate   Syntax / structure checks (no Docker required)"

env:
	@test -f .env || cp .env.example .env
	@echo ".env ready"

download:
	./scripts/download_data.sh

up: env
	docker compose --env-file .env up --build -d

down:
	docker compose --env-file .env down

logs:
	docker compose --env-file .env logs -f --tail=100

pipeline:
	@echo "Open http://localhost:8080 (admin / see .env) and trigger ecommerce_analytics_pipeline"
	@echo "Or: docker exec ecommerce-airflow airflow dags trigger ecommerce_analytics_pipeline"

test:
	python -m pytest tests/ -q

validate:
	python -m py_compile src/ingest.py airflow/dags/ecommerce_pipeline.py
	python -m pytest tests/ -q
	@test -f dbt/dbt_project.yml
	@test -f docker-compose.yml
	@echo "validate ok"
