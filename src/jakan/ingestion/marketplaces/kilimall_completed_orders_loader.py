from __future__ import annotations
from pathlib import Path
import pandas as pd
from jakan.common.ids import new_run_id, utc_now
from jakan.common.text import parse_money, clean_column_name
from jakan.common.db import insert_rows

POSITIONAL_COLUMNS = ["order_number", "order_id", "shop_id", "shop_name", "sku_id", "sku_title", "sold_qty", "deal_price", "promotion_type", "discount", "order_time", "payment_time", "complete_time", "status"]

def as_dt(value):
    if value is None or pd.isna(value):
        return None
    dt = pd.to_datetime(value, errors="coerce")
    return None if pd.isna(dt) else dt.to_pydatetime()

def as_int(value):
    """Parse a value as an integer safely, handling floats and decimals."""
    if value is None or pd.isna(value):
        return None
    try:
        # Convert to float first to handle both int and float inputs
        float_val = float(value)
        if float_val != float_val:  # NaN check
            return None
        # Round to nearest integer instead of truncating
        return int(round(float_val))
    except (ValueError, TypeError):
        return None

def load_completed_orders_excel(path: str, store_name: str) -> int:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    df = pd.read_excel(p, header=0)
    if len(df.columns) >= len(POSITIONAL_COLUMNS):
        df = df.iloc[:, :len(POSITIONAL_COLUMNS)]
        df.columns = POSITIONAL_COLUMNS
    else:
        df.columns = [clean_column_name(c) for c in df.columns]
    df = df.dropna(how="all")
    run_id, imported_at, rows = new_run_id("kilimall_orders"), utc_now(), []
    for _, rec in df.iterrows():
        raw = rec.to_dict()
        if pd.isna(raw.get("order_number")) and pd.isna(raw.get("order_id")) and pd.isna(raw.get("sku_id")):
            continue
        rows.append({
            "import_run_id": run_id,
            "imported_at": imported_at,
            "store_name": store_name,
            "order_number": None if pd.isna(raw.get("order_number")) else str(raw.get("order_number")).strip(),
            "order_id": None if pd.isna(raw.get("order_id")) else str(raw.get("order_id")).strip(),
            "sku_id": None if pd.isna(raw.get("sku_id")) else str(raw.get("sku_id")).strip(),
            "sku_title": None if pd.isna(raw.get("sku_title")) else str(raw.get("sku_title")).strip(),
            "sold_qty": as_int(raw.get("sold_qty")),
            "deal_price": parse_money(raw.get("deal_price")),
            "promotion_type": None if pd.isna(raw.get("promotion_type")) else str(raw.get("promotion_type")).strip(),
            "discount": parse_money(raw.get("discount")),
            "order_time": as_dt(raw.get("order_time")),
            "payment_time": as_dt(raw.get("payment_time")),
            "complete_time": as_dt(raw.get("complete_time")),
            "status": None if pd.isna(raw.get("status")) else str(raw.get("status")).strip(),
            "raw_payload": raw,
        })
    return insert_rows("raw.kilimall_completed_orders", rows)
