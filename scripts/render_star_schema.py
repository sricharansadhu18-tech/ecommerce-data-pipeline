#!/usr/bin/env python3
"""Render a clean Kimball star-schema diagram PNG.

Connectors are drawn first and clipped to box edges so they sit behind the tables.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parents[1] / "screenshots" / "star-schema.png"
OUT.parent.mkdir(parents=True, exist_ok=True)

W, H = 2000, 1300
BG = (247, 249, 252)
NAVY = (15, 44, 89)
TEAL = (15, 118, 110)
AMBER = (194, 65, 12)
SLATE = (51, 65, 85)
MUTED = (100, 116, 139)
WHITE = (255, 255, 255)
BORDER = (203, 213, 225)
LINE = (13, 148, 136)


def font(size, bold=False):
    path = (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    )
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def main() -> None:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    title_f = font(36, True)
    sub_f = font(18)
    head_f = font(18, True)
    body_f = font(15)
    small_f = font(13)

    d.text((80, 40), "Olist E-Commerce  ·  Kimball star schema", font=title_f, fill=NAVY)
    d.text(
        (80, 90),
        "Facts at the centre, conformed dimensions around the rim. Built in dbt from the public Olist extract.",
        font=sub_f,
        fill=MUTED,
    )

    boxes = {
        "dim_customers": (80, 200, 420, 250, "dim_customers", [
            "customer_key, customer_unique_id",
            "customer_city, customer_state",
            "first / last order date",
            "lifetime_orders, is_repeat_customer",
        ], AMBER),
        "dim_date": (1500, 200, 400, 250, "dim_date", [
            "date_key (YYYYMMDD)",
            "date_day, year, quarter, month",
            "iso_week, iso_dow, day_name",
            "is_weekend, year_month",
        ], AMBER),
        "fct_orders": (720, 380, 540, 280, "fct_orders", [
            "order_id  (degenerate)",
            "customer_key  →  dim_customers",
            "order_date_key  →  dim_date",
            "payment_total, item_count, freight",
            "is_delivered, is_late, delivery_days",
            "review_score, customer_state",
        ], NAVY),
        "fct_order_items": (720, 780, 540, 260, "fct_order_items", [
            "order_id + order_item_id",
            "product_key  →  dim_products",
            "seller_key  →  dim_sellers",
            "customer_key, order_date_key  (conformed)",
            "price, freight_value, line_total",
        ], TEAL),
        "dim_products": (80, 860, 420, 250, "dim_products", [
            "product_key, product_id",
            "product_category_name",
            "product_category_name_english",
            "weight and dimensions",
        ], AMBER),
        "dim_sellers": (1500, 860, 400, 230, "dim_sellers", [
            "seller_key, seller_id",
            "seller_city, seller_state",
            "seller_zip_code_prefix",
        ], AMBER),
    }

    def rect(name):
        x, y, w, h, *_ = boxes[name]
        return x, y, w, h

    def center(name):
        x, y, w, h = rect(name)
        return x + w / 2, y + h / 2

    def edge_point(name, toward_x, toward_y):
        x, y, w, h = rect(name)
        cx, cy = x + w / 2, y + h / 2
        dx, dy = toward_x - cx, toward_y - cy
        if dx == 0 and dy == 0:
            return cx, cy
        tx = (w / 2) / abs(dx) if dx else float("inf")
        ty = (h / 2) / abs(dy) if dy else float("inf")
        t = min(tx, ty)
        return cx + dx * t, cy + dy * t

    def connector(a, b, width=3):
        ax, ay = center(a)
        bx, by = center(b)
        x1, y1 = edge_point(a, bx, by)
        x2, y2 = edge_point(b, ax, ay)
        d.line((x1, y1, x2, y2), fill=LINE, width=width)

    connector("dim_customers", "fct_orders")
    connector("dim_date", "fct_orders")
    connector("dim_products", "fct_order_items")
    connector("dim_sellers", "fct_order_items")
    connector("fct_orders", "fct_order_items")

    def draw_box(spec):
        x, y, w, h, title, rows, color = spec
        d.rounded_rectangle((x, y, x + w, y + h), radius=14, fill=WHITE, outline=BORDER, width=2)
        d.rounded_rectangle((x, y, x + w, y + 48), radius=14, fill=color)
        d.rectangle((x, y + 24, x + w, y + 48), fill=color)
        d.text((x + 16, y + 12), title, font=head_f, fill=WHITE)
        yy = y + 64
        for row in rows:
            d.text((x + 16, yy), row, font=body_f, fill=SLATE)
            yy += 26

    for spec in boxes.values():
        draw_box(spec)

    d.text(
        (80, 1220),
        "Supporting marts: mart_monthly_revenue  ·  mart_category_performance  ·  mart_delivery_reviews  ·  mart_late_delivery_by_state",
        font=small_f,
        fill=MUTED,
    )

    img.save(OUT, "PNG")
    print(f"wrote {OUT} {img.size}")


if __name__ == "__main__":
    main()
