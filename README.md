# Jakan Phone Store Data Stack

Raw data ingestion for Kilimall and Oraimo marketplace with PostgreSQL + Metabase.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Quick Start](#quick-start)
   - [Complete Setup (One-Time)](#complete-setup-one-time)
   - [Subsequent Runs](#subsequent-runs-repeat-this-each-time)
   - [Important Notes](#important-notes)
4. [Quick Reference](#quick-reference)
5. [Starting & Stopping Services](#starting--stopping-services)
6. [Data Loading](#data-loading)
7. [CLI Commands](#cli-commands)
8. [Analytics in Metabase](#analytics-in-metabase)
9. [Troubleshooting](#troubleshooting)

---

## Project Overview

This data stack ingests product and order data from:
- **Kilimall**: Marketplace orders, inventory, and weekly statements
- **Oraimo**: Supplier product catalog and pricing

Raw data is stored in PostgreSQL. Build your own views, dashboards, and analytics in Metabase.

### Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Database** | PostgreSQL 16 | Raw data warehouse |
| **BI Tool** | Metabase | SQL queries & dashboards |
| **Ingestion** | Python + Pandas | Data loading |
| **Orchestration** | Docker Compose | Container services |

---

## Architecture

### Data Flow

```
Raw Data Sources
    ├── Kilimall Excel Exports
    │   ├── inventory → raw.kilimall_inventory
    │   ├── orders → raw.kilimall_completed_orders
    │   └── statements → raw.kilimall_weekly_statement_lines
    │
    └── Oraimo Scraper
        └── Product catalog → raw.oraimo_products

PostgreSQL (raw schema only)
    └── You build views/dashboards in Metabase
```

### Database Schema

- **raw**: All ingested source data (unmodified)

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Git

### Complete Setup (One-Time)

Follow these steps **once** to set everything up:

**Step 1: Start Services**
```bash
docker compose up -d
```
Wait 30 seconds for PostgreSQL and Metabase to be ready.

**Step 2: Setup Python Environment**
```bash
python -m venv .venv
.venv\Scripts\activate           # Windows
# OR
source .venv/bin/activate        # Linux/Mac

pip install -r requirements.txt
pip install -e .
```

**Step 3: Load All Data**
```bash
# Windows PowerShell
.\load-all.ps1

# Linux/Mac
make load-all
```

**Step 4: Configure Metabase (One-Time Only)**
1. Open `http://localhost:3000`
2. Set admin email/password (this is saved, won't ask again)
3. Database connection:
   - **Database type**: PostgreSQL
   - **Host**: `warehouse`
   - **Port**: `5432`
   - **Database**: `jakan_warehouse`
   - **Username**: `jakan`
   - **Password**: `jakan_dev_password`
4. Click "Save" and wait for metadata scan (~30 seconds)

**Step 5: Start Building Dashboards**
- Click "+" → New Question
- Select from `raw` schema tables
- Write SQL queries and visualize
- Save and add to dashboards

---

### Subsequent Runs (Repeat This Each Time)

Once setup is complete, to use the system again:

**Step 1: Start Services**
```bash
docker compose up -d
```

**Step 2: Activate Python Environment (if not already active)**
```bash
.venv\Scripts\activate           # Windows
# OR
source .venv/bin/activate        # Linux/Mac
```

**Step 3: Load New Data (if you have new files)**
```bash
# Windows PowerShell
.\load-all.ps1

# Linux/Mac
make load-all
```

**Step 4: Access Metabase**
- Open `http://localhost:3000`
- **No need to configure again** - it's already set up!
- Build queries and dashboards

---

### Important Notes

✅ **Metabase Setup is One-Time**
- Admin account: Saved and persists in Docker volume
- Database connection: Saved and persists
- You never have to configure it again

✅ **Database Initialization is One-Time**
- `python -m jakan.cli init-db` creates the raw schema
- Run it once, then just load new data with `make load-all`

✅ **Services Persist Data**
- Stop services: `docker compose down` (data stays)
- Start services: `docker compose up -d` (data is there)
- Only deleted when you run `docker compose down -v`

---

## Quick Reference

### One-Time Setup Order
1. `docker compose up -d` (start services)
2. Setup Python environment (venv + packages)
3. `.\load-all.ps1` (load all data)
4. Configure Metabase at http://localhost:3000
5. Start building dashboards!

### Every Time After That
1. `docker compose up -d` (start services)
2. `.venv\Scripts\activate` (activate Python)
3. `.\load-all.ps1` (load new data if needed)
4. Open http://localhost:3000 (just login!)

### Quick Reference Table

| Action | When | Command | Platform |
|--------|------|---------|----------|
| Start services | Every session | `docker compose up -d` | All |
| Stop services | When done | `docker compose down` | All |
| Setup Python | Once only | `python -m venv .venv` | All |
| Activate Python | Every session | `.venv\Scripts\activate` | Windows |
| | | `source .venv/bin/activate` | Linux/Mac |
| Load data | New files | `.\load-all.ps1` | Windows |
| | | `make load-all` | Linux/Mac |
| Configure Metabase | Once only | http://localhost:3000 (first visit) | All |
| Use Metabase | Always | http://localhost:3000 (just login) | All |

---

### Setup (Windows PowerShell)

```powershell
# Clone and setup
git clone <repo-url>
cd jakan-enterprises
cp .env.example .env

# Start services
docker compose up -d --build

# Setup Python environment
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .

# Initialize database
python -m jakan.cli init-db
```

### Setup (Linux/Mac)

```bash
git clone <repo-url>
cd jakan-enterprises
cp .env.example .env
docker compose up -d --build

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .

python -m jakan.cli init-db
```

### Verify Installation

```bash
# Check database
docker compose exec warehouse psql -U jakan -d jakan_warehouse -c "SELECT COUNT(*) FROM raw.kilimall_inventory"

# Access Metabase
# Navigate to http://localhost:3000
```

---

## Starting & Stopping Services

### Start Services

```bash
# Start all services (PostgreSQL, Metabase)
docker compose up -d
```

That's it! Services will run in the background.

### Stop Services

```bash
# Stop all services
docker compose down
```

### View Service Status

```bash
# See which services are running
docker compose ps
```

### View Logs

```bash
# Check logs for a specific service
docker compose logs warehouse    # PostgreSQL logs
docker compose logs metabase     # Metabase logs

# Follow logs in real-time
docker compose logs -f warehouse
```

---

## Cleaning Up Old Models

If you have old dbt models (staging, intermediate, marts schemas) that you want to remove:

### Option 1: Clean Specific Schemas (Keep Raw Data)

```bash
# Remove only the dbt-created schemas, keep raw data
docker compose exec warehouse psql -U jakan -d jakan_warehouse -c "
DROP SCHEMA IF EXISTS staging CASCADE;
DROP SCHEMA IF EXISTS intermediate CASCADE;
DROP SCHEMA IF EXISTS marts CASCADE;
"
```

### Option 2: Full Clean Slate (Remove Everything)

```bash
# Remove all data including raw tables
docker compose down -v
docker compose up -d

# Reinitialize database
python -m jakan.cli init-db
```

---

## Data Loading

### Quick Load (All at Once)

```bash
# Load everything in one command
make load-all
```

This will:
1. Initialize the database (one-time)
2. Load Kilimall inventory
3. Load Kilimall orders  
4. Scrape & load Oraimo products

**That's it!** All your raw data is now in PostgreSQL.

### Manual Loading (Step by Step)

If you need to run commands individually:

#### 1. Initialize Database (One-time)

```bash
python -m jakan.cli init-db
```

#### 2. Load Kilimall Inventory

```bash
python -m jakan.cli load-kilimall-inventory data/raw/kilimall/inventory/kilimall_inventory.xlsx --store "JAKAN PHONE STORE"
```

#### 3. Load Kilimall Orders

```bash
python -m jakan.cli load-kilimall-orders data/raw/kilimall/orders/completed_orders.xlsx --store "JAKAN PHONE STORE"
```

#### 4. Load Weekly Statements

```bash
python -m jakan.cli load-kilimall-weekly-statements data/raw/kilimall/weekly_statements
```

#### 5. Scrape & Load Oraimo Products

```bash
python -m jakan.cli scrape-oraimo --load
```

### Loading Only Specific Data

You can load or update just one type of data at any time. Use these commands as needed:

- **Load Kilimall inventory only:**
  ```powershell
  python -m jakan.cli load-kilimall-inventory data/raw/kilimall/inventory/kilimall_inventory.xlsx
  ```

- **Load Kilimall orders only:**
  ```powershell
  python -m jakan.cli load-kilimall-orders data/raw/kilimall/orders/completed_orders.xlsx
  ```

- **Load Kilimall weekly statements only:**
  ```powershell
  python -m jakan.cli load-kilimall-weekly-statements data/raw/kilimall/weekly_statements
  ```

- **Scrape and load Oraimo products only:**
  ```powershell
  python -m jakan.cli scrape-oraimo --load
  ```

You do NOT need to run the full pipeline—just run the command for the data you want to update.

---

## CLI Commands

### Quick Commands

**Windows PowerShell**:
```powershell
# Start services
docker compose up -d

# Stop services
docker compose down

# Load all data at once
.\load-all.ps1

# View service logs
docker compose logs -f
```

**Linux/Mac (Using Makefile)**:
```bash
# Start services
make up

# Stop services
make down

# Load all data at once
make load-all

# View service logs
make logs
```

### Manual Commands (All Platforms)

#### `python -m jakan.cli init-db`

**Purpose**: Initialize database schema and create raw tables.

**Output**: "Database initialized."

---

#### `python -m jakan.cli load-kilimall-inventory <path> [--store STORE_NAME]`

**Purpose**: Load Kilimall inventory from Excel.

**Arguments**:
- `path`: Path to Excel file (required)
- `--store`: Store name (default: "JAKAN PHONE STORE")

**Target table**: `raw.kilimall_inventory`

---

#### `python -m jakan.cli load-kilimall-orders <path> [--store STORE_NAME]`

**Purpose**: Load Kilimall completed orders from Excel.

**Arguments**:
- `path`: Path to Excel file (required)
- `--store`: Store name (default: "JAKAN PHONE STORE")

**Target table**: `raw.kilimall_completed_orders`

---

#### `python -m jakan.cli load-kilimall-weekly-statements <folder>`

**Purpose**: Load Kilimall settlement statements.

**Arguments**:
- `folder`: Path to folder with `.xlsx` files

**Target table**: `raw.kilimall_weekly_statement_lines`

---

#### `python -m jakan.cli scrape-oraimo [--load]`

**Purpose**: Scrape Oraimo products from Kilimall listings.

**Arguments**:
- `--load`: (Optional) Save to database

**Target table**: `raw.oraimo_products`

**Performance**: ~15-30 minutes

---

## Analytics in Metabase

### Getting Started

1. Open `http://localhost:3000`
2. First-time setup:
   - Set admin email/password
   - **Database**: PostgreSQL
   - **Host**: `warehouse` (Docker) or `localhost`
   - **Port**: `5432`
   - **Database**: `jakan_warehouse`
   - **User**: `jakan`
   - **Password**: `jakan_dev_password`
3. Create queries from the raw schema tables
4. Build dashboards

### Sample Queries

**Latest Oraimo Products**
```sql
SELECT * FROM raw.oraimo_products 
WHERE scraped_at = (SELECT MAX(scraped_at) FROM raw.oraimo_products)
ORDER BY supplier_title
LIMIT 50
```

**Recent Kilimall Orders**
```sql
SELECT 
  order_number,
  sku_title,
  sold_qty,
  deal_price,
  (sold_qty * deal_price) as gross_sales,
  status,
  complete_time
FROM raw.kilimall_completed_orders
ORDER BY complete_time DESC
LIMIT 100
```

**Inventory Status Summary**
```sql
SELECT 
  o.category,
  COUNT(*) as product_count,
  SUM(CASE WHEN o.stock_status = 'instock' THEN 1 ELSE 0 END) as in_stock
FROM raw.oraimo_products o
WHERE o.scraped_at = (SELECT MAX(scraped_at) FROM raw.oraimo_products)
GROUP BY o.category
ORDER BY in_stock DESC
```

---

## Troubleshooting

### Container Issues

**PostgreSQL not starting**:
```bash
docker compose logs warehouse
docker compose down -v
docker compose up -d
```

**Metabase connection failing**:
```bash
docker compose exec warehouse pg_isready -U jakan
docker compose logs metabase
```

### Data Loading Issues

**File not found**:
```bash
ls -la data/raw/kilimall/
```

**Duplicate key errors**:
```bash
# Clear and reload
docker compose exec warehouse psql -U jakan -d jakan_warehouse \
  -c "TRUNCATE raw.kilimall_inventory CASCADE;"
```

### Database Access

**Direct SQL queries**:
```bash
docker compose exec warehouse psql -U jakan -d jakan_warehouse
```

---

## Project Structure

```
jakan-enterprises/
├── data/
│   ├── raw/
│   │   └── kilimall/
│   │       ├── inventory/
│   │       ├── orders/
│   │       └── weekly_statements/
│   ├── exports/
│   └── manual/
├── sql/
│   ├── 00_create_schemas.sql
│   └── 01_create_raw_tables.sql
├── src/
│   └── jakan/
│       ├── cli.py
│       ├── ingestion/
│       │   ├── marketplaces/
│       │   │   ├── kilimall_inventory_loader.py
│       │   │   ├── kilimall_orders_loader.py
│       │   │   └── kilimall_weekly_statement_loader.py
│       │   └── suppliers/
│       │       └── oraimo_scraper.py
│       ├── common/
│       │   ├── config.py
│       │   └── db.py
│       └── matching/
│           └── mapping_review.py
├── docker-compose.yml
├── Makefile
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## Support

For issues:
1. Check Docker logs: `docker compose logs <service>`
2. Query PostgreSQL directly: `docker compose exec warehouse psql -U jakan -d jakan_warehouse`
3. Verify data: `SELECT COUNT(*) FROM raw.oraimo_products;`
