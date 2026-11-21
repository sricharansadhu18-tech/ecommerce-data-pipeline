#!/usr/bin/env python3
"""Load the public Olist Brazilian E-Commerce CSVs into the Postgres `raw` schema."""

from __future__ import annotations

import os
import sys
from pathlib import Path

DEFAULT_DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"

# (csv filename, raw table, create-table SQL)
TABLES = [
    (
        "olist_orders_dataset.csv",
        "orders",
        """
        CREATE TABLE raw.orders (
            order_id                       text PRIMARY KEY,
            customer_id                    text NOT NULL,
            order_status                   text NOT NULL,
            order_purchase_timestamp       timestamp,
            order_approved_at              timestamp,
            order_delivered_carrier_date   timestamp,
            order_delivered_customer_date  timestamp,
            order_estimated_delivery_date  timestamp
        )
        """,
    ),
    (
        "olist_order_items_dataset.csv",
        "order_items",
        """
        CREATE TABLE raw.order_items (
            order_id             text NOT NULL,
            order_item_id        integer NOT NULL,
            product_id           text NOT NULL,
            seller_id            text NOT NULL,
            shipping_limit_date  timestamp,
            price                numeric(12, 2) NOT NULL,
            freight_value        numeric(12, 2) NOT NULL,
            PRIMARY KEY (order_id, order_item_id)
        )
        """,
    ),
    (
        "olist_customers_dataset.csv",
        "customers",
        """
        CREATE TABLE raw.customers (
            customer_id              text PRIMARY KEY,
            customer_unique_id       text NOT NULL,
            customer_zip_code_prefix text,
            customer_city            text,
            customer_state           text
        )
        """,
    ),
    (
        "olist_products_dataset.csv",
        "products",
        """
        CREATE TABLE raw.products (
            product_id                 text PRIMARY KEY,
            product_category_name      text,
            product_name_lenght        integer,
            product_description_lenght integer,
            product_photos_qty         integer,
            product_weight_g           numeric,
            product_length_cm          numeric,
            product_height_cm          numeric,
            product_width_cm           numeric
        )
        """,
    ),
    (
        "olist_sellers_dataset.csv",
        "sellers",
        """
        CREATE TABLE raw.sellers (
            seller_id              text PRIMARY KEY,
            seller_zip_code_prefix text,
            seller_city            text,
            seller_state           text
        )
        """,
    ),
    (
        "olist_order_payments_dataset.csv",
        "order_payments",
        """
        CREATE TABLE raw.order_payments (
            order_id             text NOT NULL,
            payment_sequential   integer NOT NULL,
            payment_type         text,
            payment_installments integer,
            payment_value        numeric(12, 2) NOT NULL,
            PRIMARY KEY (order_id, payment_sequential)
        )
        """,
    ),
    (
        "olist_order_reviews_dataset.csv",
        "order_reviews",
        """
        CREATE TABLE raw.order_reviews (
            review_id               text NOT NULL,
            order_id                text NOT NULL,
            review_score            integer,
            review_comment_title    text,
            review_comment_message  text,
            review_creation_date    timestamp,
            review_answer_timestamp timestamp
        )
        """,
    ),
    (
        "olist_geolocation_dataset.csv",
        "geolocation",
        """
        CREATE TABLE raw.geolocation (
            geolocation_zip_code_prefix text,
            geolocation_lat             numeric,
            geolocation_lng             numeric,
            geolocation_city            text,
            geolocation_state           text
        )
        """,
    ),
    (
        "product_category_name_translation.csv",
        "product_category_translation",
        """
        CREATE TABLE raw.product_category_translation (
            product_category_name         text PRIMARY KEY,
            product_category_name_english text NOT NULL
        )
        """,
    ),
]


def connect():
    import psycopg2

    return psycopg2.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=os.environ.get("PGPORT", "5432"),
        user=os.environ.get("PGUSER", "ecommerce"),
        password=os.environ.get("PGPASSWORD", "ecommerce"),
        dbname=os.environ.get("PGDATABASE", "ecommerce"),
    )


def load_table(cur, data_dir: Path, filename: str, table: str, ddl: str) -> int:
    path = data_dir / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing extract: {path}")
    cur.execute(f"DROP TABLE IF EXISTS raw.{table} CASCADE;")
    cur.execute(ddl)
    with path.open("r", encoding="utf-8", newline="") as fh:
        cur.copy_expert(
            f"COPY raw.{table} FROM STDIN WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')",
            fh,
        )
    cur.execute(f"SELECT count(*) FROM raw.{table};")
    return int(cur.fetchone()[0])


def main() -> int:
    data_dir = Path(os.environ.get("OLIST_DATA_DIR", DEFAULT_DATA_DIR))
    print(f"[ingest] reading CSVs from {data_dir}")
    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute("CREATE SCHEMA IF NOT EXISTS raw;")
            for filename, table, ddl in TABLES:
                n = load_table(cur, data_dir, filename, table, ddl)
                print(f"[ingest] raw.{table}: {n:,} rows")
        conn.commit()
    finally:
        conn.close()
    print("[ingest] done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
