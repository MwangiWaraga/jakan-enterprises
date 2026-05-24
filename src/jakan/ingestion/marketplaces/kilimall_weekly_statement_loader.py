from __future__ import annotations
from pathlib import Path
from datetime import datetime
import glob
import pandas as pd
from jakan.common.ids import new_run_id, utc_now
from jakan.common.text import clean_column_name, parse_money
from jakan.common.db import insert_rows

def parse_filename_dates(filename: str):
    try:
        parts = Path(filename).name.split("_")
        if len(parts) >= 2 and len(parts[0]) == 8 and len(parts[1]) == 8:
            return datetime.strptime(parts[0], "%Y%m%d").date(), datetime.strptime(parts[1], "%Y%m%d").date()
    except Exception:
        pass
    return None, None

def pick(raw: dict, names: list[str]):
    for name in names:
        if name in raw and pd.notnull(raw[name]):
            return raw[name]
    return None

def as_dt(value):
    if value is None or pd.isna(value):
        return None
    dt = pd.to_datetime(value, errors="coerce")
    return None if pd.isna(dt) else dt.to_pydatetime()

def load_weekly_statements_folder(folder_path: str) -> int:
    files = glob.glob(str(Path(folder_path) / "*.xlsx"))
    if not files:
        raise FileNotFoundError(f"No .xlsx files found in {folder_path}")
    run_id, imported_at, rows = new_run_id("kilimall_weekly_statement"), utc_now(), []
    for file in files:
        start_date, end_date = parse_filename_dates(file)
        xls = pd.ExcelFile(file)
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            if df.empty:
                continue
            df.columns = [clean_column_name(c) for c in df.columns]
            df = df.loc[:, ~df.columns.duplicated()].copy().dropna(how="all")
            for _, rec in df.iterrows():
                raw = rec.to_dict()
                order_sn = pick(raw, ["order_sn", "order_number", "order_no", "order_id"])
                goods_id = pick(raw, ["goods_id", "sku_id", "sku", "product_id"])
                rows.append({
                    "import_run_id": run_id,
                    "imported_at": imported_at,
                    "source_filename": Path(file).name,
                    "sheet_name": sheet_name,
                    "statement_start_date": start_date,
                    "statement_end_date": end_date,
                    "store_id": pick(raw, ["store_id"]),
                    "store_name": pick(raw, ["store_name", "shop_name"]),
                    "order_sn": None if pd.isna(order_sn) else str(order_sn).strip().lstrip(","),
                    "payment_time": as_dt(pick(raw, ["payment_time"])),
                    "finished_time": as_dt(pick(raw, ["finished_time", "finnshed_time", "complete_time"])),
                    "goods_id": None if pd.isna(goods_id) else str(goods_id).strip(),
                    "goods_name": None if pd.isna(pick(raw, ["goods_name", "sku_title", "product_name", "title"])) else str(pick(raw, ["goods_name", "sku_title", "product_name", "title"])).strip(),
                    "goods_price": parse_money(pick(raw, ["goods_price", "deal_price"])),
                    "goods_num": int(parse_money(pick(raw, ["goods_num", "sold_qty"])) or 0),
                    "complete_amount": parse_money(pick(raw, ["complete_amount", "total_valume", "total_volume"])),
                    "commission": parse_money(pick(raw, ["commission", "total_commission"])),
                    "ds_quality_inspection_fee": parse_money(pick(raw, ["ds_quality_inspection_fee"])),
                    "fine": parse_money(pick(raw, ["fine"])),
                    "warehouse_operation_fee": parse_money(pick(raw, ["warehouse_operation_fee", "operation_fee"])),
                    "warehouse_storage_fee": parse_money(pick(raw, ["warehouse_storage_fee", "storage_fee"])),
                    "ds_processing_fee": parse_money(pick(raw, ["ds_processing_fee"])),
                    "lite_shipping_fee": parse_money(pick(raw, ["lite_shipping_fee", "ds_shipping_fee"])),
                    "customer_service_discount_fee": parse_money(pick(raw, ["customer_service_discount_fee", "customer_service_discount"])),
                    "other_deductions": parse_money(pick(raw, ["other_deductions"])),
                    "billing_appeal": parse_money(pick(raw, ["billing_appeal"])),
                    "compensations": parse_money(pick(raw, ["compensations", "compensation"])),
                    "settlement_payable": parse_money(pick(raw, ["settlement_payable", "settlement"])),
                    "raw_payload": raw,
                })
    return insert_rows("raw.kilimall_weekly_statement_lines", rows)
