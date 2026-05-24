from __future__ import annotations
from datetime import datetime, timezone
import uuid

def new_run_id(prefix: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}_{stamp}_{uuid.uuid4().hex[:8]}"

def utc_now():
    return datetime.now(timezone.utc)
