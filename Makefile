.PHONY: up down logs init load-all scrape

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

init:
	python -m jakan.cli init-db

load-all: init
	python -m jakan.cli load-kilimall-inventory data/raw/kilimall/inventory/kilimall_inventory.xlsx
	python -m jakan.cli load-kilimall-orders data/raw/kilimall/orders/completed_orders.xlsx
	python -m jakan.cli scrape-oraimo --load
	@echo "✅ All data loaded successfully!"

scrape:
	python -m jakan.cli scrape-oraimo --load
