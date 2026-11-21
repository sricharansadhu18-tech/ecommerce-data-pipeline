"""Unit tests for the Olist ingest module (no database required)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INGEST = ROOT / "src" / "ingest.py"


def _load_ingest():
    spec = importlib.util.spec_from_file_location("ecommerce_ingest", INGEST)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_expected_tables_and_files():
    mod = _load_ingest()
    names = [table for _, table, _ in mod.TABLES]
    files = [filename for filename, _, _ in mod.TABLES]

    assert len(mod.TABLES) == 9
    assert names == [
        "orders",
        "order_items",
        "customers",
        "products",
        "sellers",
        "order_payments",
        "order_reviews",
        "geolocation",
        "product_category_translation",
    ]
    assert all(f.endswith(".csv") for f in files)
    assert "olist_orders_dataset.csv" in files


def test_default_data_dir_points_at_repo_raw():
    mod = _load_ingest()
    assert mod.DEFAULT_DATA_DIR.name == "raw"
    assert mod.DEFAULT_DATA_DIR.parent.name == "data"
