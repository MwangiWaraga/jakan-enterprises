from __future__ import annotations
from pathlib import Path
import pandas as pd
from jakan.common.ids import new_run_id, utc_now
from jakan.common.text import parse_money, clean_column_name
from jakan.common.db import insert_rows

def pick(row: dict, candidates: list[str], default=None):
    for c in candidates:
        if c in row and pd.notnull(row[c]):
            return row[c]
    return default

def load_inventory_excel(path: str, store_name: str) -> int:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    df = pd.read_excel(p)
    df.columns = [clean_column_name(c) for c in df.columns]
    df = df.dropna(how="all")
    run_id, imported_at, rows = new_run_id("kilimall_inventory"), utc_now(), []
    for _, rec in df.iterrows():
        raw = rec.to_dict()
        listing_id = pick(raw, ["listing_id", "listingid", "listing"])
        sku_id = pick(raw, ["sku_id", "skuid", "sku"])
        title = pick(raw, ["title", "product_title", "kil_title", "product_name"])
        if pd.isna(listing_id) and pd.isna(sku_id) and pd.isna(title):
            continue
        rows.append({
            "import_run_id": run_id,
            "imported_at": imported_at,
            "store_name": store_name,
            "marketplace": "KILIMALL",
            "listing_id": "" if pd.isna(listing_id) else str(listing_id).strip(),
            "sku_id": "" if pd.isna(sku_id) else str(sku_id).strip(),
            "vendor_product_id": "" if pd.isna(pick(raw, ["vendor_product_id", "vendor_productid", "vendor_sku", "seller_sku"])) else str(pick(raw, ["vendor_product_id", "vendor_productid", "vendor_sku", "seller_sku"])).strip(),
            "title": "" if pd.isna(title) else str(title).strip(),
            "kilimall_url": "" if pd.isna(pick(raw, ["kil_url", "url", "product_url", "listing_url"])) else str(pick(raw, ["kil_url", "url", "product_url", "listing_url"])).strip(),
            "selling_price": parse_money(pick(raw, ["selling_price", "current_kil_sp", "price", "sale_price"])),
            "fbk_inventory": parse_money(pick(raw, ["fbk_inventory", "fbk_stock"])),
            "non_fbk_inventory": parse_money(pick(raw, ["non_fbk_inventory", "non_fbk_stock", "stock"])),
            "status": "" if pd.isna(pick(raw, ["status", "listing_status", "product_status"])) else str(pick(raw, ["status", "listing_status", "product_status"])).strip(),
            "raw_payload": raw,
        })
    return insert_rows("raw.kilimall_inventory", rows)
