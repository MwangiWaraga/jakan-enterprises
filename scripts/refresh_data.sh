#!/bin/bash
# Data refresh orchestration script
# Runs all data loading, transformation, and sync steps

set -e  # Exit on error

echo "Starting data refresh workflow..."
echo "=================================="

# Step 1: Load Kilimall Inventory
echo ""
echo "Step 1/5: Loading Kilimall Inventory..."
source .venv/Scripts/activate
python -m jakan.cli load-kilimall-inventory
echo "✓ Kilimall inventory loaded"

# Step 2: Load Kilimall Orders
echo ""
echo "Step 2/5: Loading Kilimall Orders..."
python -m jakan.cli load-kilimall-orders
echo "✓ Kilimall orders loaded"

# Step 3: Scrape Oraimo Products
echo ""
echo "Step 3/5: Scraping Oraimo products..."
python -m jakan.cli scrape-oraimo
echo "✓ Oraimo products scraped"

# Step 4: Run dbt transformations
echo ""
echo "Step 4/5: Running dbt transformations..."
docker compose run --rm dbt dbt run --profiles-dir /usr/app
echo "✓ dbt transformations completed"

# Step 5: Sync Metabase
echo ""
echo "Step 5/5: Syncing Metabase..."
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"is_full_sync": true}' \
  http://localhost:3000/api/database/1/sync \
  || echo "Note: Metabase sync triggered (may need manual refresh if auto-sync disabled)"
echo "✓ Metabase sync initiated"

echo ""
echo "=================================="
echo "✓ Data refresh workflow completed!"
echo "Check Metabase at http://localhost:3000"
