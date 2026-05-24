# Jakan Phone Store Data Stack MVP

Local-first data stack for Jakan Phone Store dropshipping operations.

## Stack

- **Postgres**: local warehouse
- **dbt Core**: transformations
- **Metabase**: dashboards
- **Python**: scraping/loading
- **Docker Compose**: local services

## Main MVP outputs

- OSS items to delist
- Not posted items to post
- Restocked inactive items to reactivate
- Price updates needed
- Kilimall order profitability with fees/fines

## Quick start

```bash
cp .env.example .env
docker compose up -d --build

python -m venv .venv
source .venv/bin/activate          # Mac/Linux
# .venv\Scripts\activate         # Windows PowerShell
pip install -r requirements.txt
pip install -e .

python -m jakan.cli init-db
python -m jakan.cli scrape-oraimo --load
```

Load Kilimall inventory:

```bash
python -m jakan.cli load-kilimall-inventory data/raw/kilimall/inventory/kilimall_inventory.xlsx --store "JAKAN PHONE STORE"
```

Load Kilimall completed orders:

```bash
python -m jakan.cli load-kilimall-orders data/raw/kilimall/orders/completed_orders.xlsx --store "JAKAN PHONE STORE"
```

Load Kilimall weekly statements:

```bash
python -m jakan.cli load-kilimall-weekly-statements data/raw/kilimall/weekly_statements
```

Build mapping review:

```bash
python -m jakan.cli build-mapping-review
```

Run dbt:

```bash
cd dbt/jakan_analytics
dbt seed --profiles-dir .
dbt run --profiles-dir .
dbt test --profiles-dir .
```

Or with Docker:

```bash
docker compose run --rm dbt dbt seed --profiles-dir /usr/app
docker compose run --rm dbt dbt run --profiles-dir /usr/app
docker compose run --rm dbt dbt test --profiles-dir /usr/app
```

## Metabase

Open:

```text
http://localhost:3000
```

Connect to warehouse:

```text
Host: warehouse
Port: 5432
Database: jakan_warehouse
Username: jakan
Password: jakan_dev_password
Schema: marts
```

## Identity rule

Fuzzy matching is only for review. The final joins should use:

```text
dbt/jakan_analytics/seeds/sku_source_map.csv
dbt/jakan_analytics/seeds/sku_listing_map.csv
```

Use Oraimo key priority:

```text
ean → model → slug → url_hash
```

Use Kilimall `sku_id` as the marketplace SKU key.
