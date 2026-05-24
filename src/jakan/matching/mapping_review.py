from __future__ import annotations
from pathlib import Path
import pandas as pd
from rapidfuzz import fuzz, process
from jakan.common.db import fetch_all
from jakan.common.text import normalize_title

def build_mapping_review(output_path: str = "data/exports/mapping_review/sku_mapping_review.csv") -> str:
    oraimo = fetch_all('''
        SELECT DISTINCT ON (source_product_key)
            source_product_key, title AS oraimo_title, product_url AS oraimo_url,
            price_now_num, stock_status, category
        FROM raw.oraimo_products
        ORDER BY source_product_key, scraped_at DESC
    ''')
    kilimall = fetch_all('''
        SELECT DISTINCT ON (store_name, sku_id)
            store_name, listing_id, sku_id, vendor_product_id,
            title AS kilimall_title, kilimall_url, selling_price, status
        FROM raw.kilimall_inventory
        WHERE COALESCE(sku_id, '') <> ''
        ORDER BY store_name, sku_id, imported_at DESC
    ''')
    if not oraimo or not kilimall:
        raise RuntimeError("Need both Oraimo scrape and Kilimall inventory before building mapping review.")
    oraimo_df, kil_df = pd.DataFrame(oraimo), pd.DataFrame(kilimall)
    choices = {normalize_title(row["oraimo_title"]): i for i, row in oraimo_df.iterrows() if row.get("oraimo_title")}
    rows = []
    for _, k in kil_df.iterrows():
        match = process.extractOne(normalize_title(k.get("kilimall_title")), list(choices.keys()), scorer=fuzz.token_set_ratio)
        if match:
            matched_norm, score, _ = match
            o = oraimo_df.iloc[choices[matched_norm]].to_dict()
        else:
            score, o = 0, {}
        rows.append({
            "review_status": "TODO",
            "confidence_score": score,
            "suggested_match_method": "FUZZY_TITLE",
            "store_name": k.get("store_name"),
            "listing_id": k.get("listing_id"),
            "sku_id": k.get("sku_id"),
            "vendor_product_id": k.get("vendor_product_id"),
            "kilimall_title": k.get("kilimall_title"),
            "kilimall_url": k.get("kilimall_url"),
            "kilimall_selling_price": k.get("selling_price"),
            "kilimall_status": k.get("status"),
            "source_product_key": o.get("source_product_key"),
            "oraimo_title": o.get("oraimo_title"),
            "oraimo_url": o.get("oraimo_url"),
            "oraimo_price_now": o.get("price_now_num"),
            "oraimo_stock_status": o.get("stock_status"),
            "notes": "",
        })
    out = pd.DataFrame(rows).sort_values("confidence_score", ascending=False)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_path, index=False)
    return output_path
