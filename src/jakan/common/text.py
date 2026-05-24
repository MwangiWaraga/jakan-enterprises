from __future__ import annotations
import re
from decimal import Decimal
from urllib.parse import urlparse, parse_qs
import hashlib

def parse_money(value) -> Decimal | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in ("nan", "nat", "none"):
        return None
    cleaned = re.sub(r"[^0-9.\-]", "", text)
    if cleaned in ("", ".", "-", "-."):
        return None
    try:
        return Decimal(cleaned)
    except Exception:
        return None

def normalize_title(value: str | None) -> str:
    if not value:
        return ""
    text = value.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def stable_url_hash(url: str | None) -> str:
    return hashlib.sha1((url or "").strip().lower().encode("utf-8")).hexdigest()[:16]

def clean_column_name(name: str) -> str:
    text = str(name).strip().lower().replace("（", "(").replace("）", ")")
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")

def make_source_product_key(ean: str | None, model: str | None, slug: str | None, url: str | None) -> str:
    if (ean or "").strip():
        return f"ean:{ean.strip()}"
    if (model or "").strip():
        return f"model:{model.strip()}"
    if (slug or "").strip():
        return f"slug:{slug.strip()}"
    return f"url_hash:{stable_url_hash(url)}"
