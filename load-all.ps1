# Load all data into the warehouse

Write-Host "================================" -ForegroundColor Green
Write-Host "Starting data load pipeline..." -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

# Step 1: Initialize database
Write-Host "`n[1/4] Initializing database..." -ForegroundColor Yellow
python -m jakan.cli init-db

# Step 2: Load Kilimall inventory
Write-Host "`n[2/4] Loading Kilimall inventory..." -ForegroundColor Yellow
python -m jakan.cli load-kilimall-inventory data/raw/kilimall/inventory/kilimall_inventory.xlsx

# Step 3: Load Kilimall orders
Write-Host "`n[3/4] Loading Kilimall orders..." -ForegroundColor Yellow
python -m jakan.cli load-kilimall-orders data/raw/kilimall/orders/completed_orders.xlsx

# Step 4: Scrape and load Oraimo products
Write-Host "`n[4/4] Scraping and loading Oraimo products..." -ForegroundColor Yellow
Write-Host "(This may take 15-30 minutes)" -ForegroundColor Cyan
python -m jakan.cli scrape-oraimo --load

Write-Host "`n================================" -ForegroundColor Green
Write-Host "✅ All data loaded successfully!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host "`nAccess Metabase at: http://localhost:3000" -ForegroundColor Cyan
