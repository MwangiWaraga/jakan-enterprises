from __future__ import annotations
import argparse, logging
from pathlib import Path
from jakan.common.db import run_sql_file
from jakan.ingestion.suppliers.oraimo_scraper import scrape_all_categories, load_oraimo_to_postgres
from jakan.ingestion.marketplaces.kilimall_inventory_loader import load_inventory_excel
from jakan.ingestion.marketplaces.kilimall_completed_orders_loader import load_completed_orders_excel
from jakan.ingestion.marketplaces.kilimall_weekly_statement_loader import load_weekly_statements_folder
from jakan.matching.mapping_review import build_mapping_review

def cmd_init_db(args):
    for sql_file in sorted(Path("sql").glob("*.sql")):
        print(f"Running {sql_file}")
        run_sql_file(str(sql_file))
    print("Database initialized.")

def cmd_scrape_oraimo(args):
    rows = scrape_all_categories()
    print(f"Scraped {len(rows)} Oraimo rows.")
    if args.load:
        print(f"Inserted {load_oraimo_to_postgres(rows)} rows into raw.oraimo_products.")

def cmd_load_inventory(args):
    print(f"Inserted {load_inventory_excel(args.path, args.store)} rows into raw.kilimall_inventory.")

def cmd_load_orders(args):
    print(f"Inserted {load_completed_orders_excel(args.path, args.store)} rows into raw.kilimall_completed_orders.")

def cmd_load_weekly(args):
    print(f"Inserted {load_weekly_statements_folder(args.folder)} rows into raw.kilimall_weekly_statement_lines.")

def cmd_mapping_review(args):
    print(f"Mapping review written to {build_mapping_review(args.output)}")

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
    parser = argparse.ArgumentParser("jakan")
    sub = parser.add_subparsers(required=True)
    p = sub.add_parser("init-db"); p.set_defaults(func=cmd_init_db)
    p = sub.add_parser("scrape-oraimo"); p.add_argument("--load", action="store_true"); p.set_defaults(func=cmd_scrape_oraimo)
    p = sub.add_parser("load-kilimall-inventory"); p.add_argument("path"); p.add_argument("--store", default="JAKAN PHONE STORE"); p.set_defaults(func=cmd_load_inventory)
    p = sub.add_parser("load-kilimall-orders"); p.add_argument("path"); p.add_argument("--store", default="JAKAN PHONE STORE"); p.set_defaults(func=cmd_load_orders)
    p = sub.add_parser("load-kilimall-weekly-statements"); p.add_argument("folder"); p.set_defaults(func=cmd_load_weekly)
    p = sub.add_parser("build-mapping-review"); p.add_argument("--output", default="data/exports/mapping_review/sku_mapping_review.csv"); p.set_defaults(func=cmd_mapping_review)
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
