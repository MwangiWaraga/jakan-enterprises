from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass(frozen=True)
class WarehouseConfig:
    host: str
    port: int
    db: str
    user: str
    password: str

def load_config() -> WarehouseConfig:
    load_dotenv()
    return WarehouseConfig(
        host=os.getenv("WAREHOUSE_HOST", "localhost"),
        port=int(os.getenv("WAREHOUSE_PORT", "5432")),
        db=os.getenv("WAREHOUSE_DB", "jakan_warehouse"),
        user=os.getenv("WAREHOUSE_USER", "jakan"),
        password=os.getenv("WAREHOUSE_PASSWORD", "jakan_dev_password"),
    )

def get_env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    return default if value in (None, "") else float(value)
