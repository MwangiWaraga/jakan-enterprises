.PHONY: up down logs init scrape dbt-seed dbt-run dbt-test dbt-build

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

init:
	python -m jakan.cli init-db

scrape:
	python -m jakan.cli scrape-oraimo --load

dbt-seed:
	docker compose run --rm dbt dbt seed --profiles-dir /usr/app

dbt-run:
	docker compose run --rm dbt dbt run --profiles-dir /usr/app

dbt-test:
	docker compose run --rm dbt dbt test --profiles-dir /usr/app

dbt-build:
	docker compose run --rm dbt dbt build --profiles-dir /usr/app
