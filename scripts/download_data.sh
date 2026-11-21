#!/usr/bin/env bash
# Download the Olist Brazilian E-Commerce CSVs from Olist's public GitHub mirror.
set -euo pipefail
DEST="$(cd "$(dirname "$0")/.." && pwd)/data/raw"
mkdir -p "$DEST"
BASE="https://raw.githubusercontent.com/olist/work-at-olist-data/master/datasets"
FILES=(
  olist_orders_dataset.csv
  olist_order_items_dataset.csv
  olist_customers_dataset.csv
  olist_products_dataset.csv
  olist_sellers_dataset.csv
  olist_order_payments_dataset.csv
  olist_order_reviews_dataset.csv
  olist_geolocation_dataset.csv
  product_category_name_translation.csv
)
for f in "${FILES[@]}"; do
  echo "Downloading $f ..."
  curl -fsSL --retry 5 --retry-delay 2 -o "$DEST/$f" "$BASE/$f"
done
echo "Done. Files in $DEST:"
wc -l "$DEST"/*.csv
