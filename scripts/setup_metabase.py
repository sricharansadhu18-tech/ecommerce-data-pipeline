#!/usr/bin/env python3
"""Create the Olist Metabase dashboard via the REST API."""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:3000"
EMAIL = "sri.charan@localhost.local"
PASSWORD = "EcommerceAnalytics1!"
SESSION = None


def req(method: str, path: str, body=None, session=None):
    data = None if body is None else json.dumps(body).encode()
    headers = {"Content-Type": "application/json"}
    token = session if session is not None else SESSION
    if token:
        headers["X-Metabase-Session"] = token
    request = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=60) as resp:
            raw = resp.read()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        try:
            parsed = json.loads(raw) if raw else {}
        except Exception:
            parsed = {"raw": raw.decode("utf-8", "replace")}
        return exc.code, parsed


def wait_health() -> None:
    for i in range(60):
        try:
            status, body = req("GET", "/api/health")
            if status == 200 and body.get("status") == "ok":
                print("Metabase is healthy")
                return
        except Exception as exc:
            print(f"waiting for Metabase ({exc})")
        time.sleep(3)
    raise SystemExit("Metabase did not become healthy")


def setup_or_login() -> str:
    _, props = req("GET", "/api/session/properties")
    if not props.get("has-user-setup"):
        token = props.get("setup-token")
        payload = {
            "token": token,
            "user": {
                "first_name": "Sri",
                "last_name": "Charan",
                "email": EMAIL,
                "password": PASSWORD,
                "site_name": "Olist E-Commerce Analytics",
            },
            "prefs": {
                "site_name": "Olist E-Commerce Analytics",
                "site_locale": "en",
                "allow_tracking": False,
            },
        }
        status, body = req("POST", "/api/setup", payload)
        print("setup", status, {k: body.get(k) for k in ("id", "errors", "message") if isinstance(body, dict)})
        if status not in (200, 201) or not body.get("id"):
            # fall through to login if a race already set up
            pass
        else:
            return body["id"]
    status, body = req("POST", "/api/session", {"username": EMAIL, "password": PASSWORD})
    if status != 200 or not body.get("id"):
        raise SystemExit(f"login failed: {status} {body}")
    return body["id"]


def ensure_database(session: str) -> int:
    _, dbs = req("GET", "/api/database", session=session)
    data = dbs.get("data", dbs) if isinstance(dbs, dict) else dbs
    for db in data:
        if db.get("name") == "Olist Warehouse":
            print("database exists", db["id"])
            return db["id"]
    status, body = req(
        "POST",
        "/api/database",
        {
            "engine": "postgres",
            "name": "Olist Warehouse",
            "details": {
                "host": "postgres",
                "port": 5432,
                "dbname": "ecommerce",
                "user": "ecommerce",
                "password": "ecommerce",
                "ssl": False,
                "schema-filters-type": "inclusion",
                "schema-filters-patterns": "marts",
            },
            "is_full_sync": True,
            "is_on_demand": False,
        },
        session=session,
    )
    print("create database", status, body.get("id") or body)
    if status not in (200, 201):
        raise SystemExit(f"database create failed: {body}")
    db_id = body["id"]
    # kick a sync and wait briefly
    req("POST", f"/api/database/{db_id}/sync_schema", {}, session=session)
    time.sleep(5)
    return db_id


def create_card(db_id: int, name: str, sql: str, display: str, viz=None) -> int:
    payload = {
        "name": name,
        "dataset_query": {
            "type": "native",
            "native": {"query": sql},
            "database": db_id,
        },
        "display": display,
        "visualization_settings": viz or {},
    }
    status, body = req("POST", "/api/card", payload)
    if status not in (200, 201):
        raise SystemExit(f"card {name} failed: {status} {body}")
    print("card", name, body["id"])
    return body["id"]


def main() -> int:
    global SESSION
    wait_health()
    SESSION = setup_or_login()
    print("session ok")
    db_id = ensure_database(SESSION)

    cards = {}
    cards["orders"] = create_card(
        db_id, "Orders",
        "select count(*) as orders from marts.fct_orders",
        "scalar",
    )
    cards["gmv"] = create_card(
        db_id, "Payment volume (R$)",
        "select round(sum(payment_total)::numeric, 2) as payment_total from marts.fct_orders",
        "scalar",
        {"scalar.currency": "BRL"},
    )
    cards["aov"] = create_card(
        db_id, "Average order value (R$)",
        "select round((sum(payment_total)/nullif(count(*),0))::numeric, 2) as aov from marts.fct_orders",
        "scalar",
    )
    cards["repeat"] = create_card(
        db_id, "Repeat customer rate",
        "select round(100.0 * avg(is_repeat_customer::int), 2) as repeat_pct from marts.dim_customers",
        "scalar",
    )
    cards["late"] = create_card(
        db_id, "Late delivery rate",
        """select round(100.0 * avg(is_late::int) filter (
              where is_delivered and is_late is not null
           ), 1) as late_rate_pct
           from marts.fct_orders""",
        "scalar",
    )
    cards["review"] = create_card(
        db_id, "Average review score",
        "select round(avg(review_score)::numeric, 2) as avg_review from marts.fct_orders where review_score is not null",
        "scalar",
    )
    cards["revenue"] = create_card(
        db_id, "Monthly payment volume",
        """select year_month, payment_total, orders, aov
           from marts.mart_monthly_revenue
           where year_month between '2017-01' and '2018-08'
           order by year_month""",
        "line",
        {"graph.dimensions": ["year_month"], "graph.metrics": ["payment_total"]},
    )
    cards["categories"] = create_card(
        db_id, "Top categories by merchandise revenue",
        """select replace(category, '_', ' ') as category,
                  merchandise_revenue,
                  orders
           from marts.mart_category_performance
           where category is not null
           order by merchandise_revenue desc
           limit 10""",
        "row",
        {"graph.dimensions": ["category"], "graph.metrics": ["merchandise_revenue"]},
    )
    cards["delivery_review"] = create_card(
        db_id, "Delivery time and late rate by review score",
        """select review_score,
                  avg_delivery_days,
                  late_rate_pct,
                  delivered_orders
           from marts.mart_delivery_reviews
           order by review_score""",
        "bar",
        {"graph.dimensions": ["review_score"], "graph.metrics": ["avg_delivery_days"]},
    )
    cards["late_state"] = create_card(
        db_id, "Late delivery rate by state",
        """select customer_state,
                  late_rate_pct,
                  delivered_orders,
                  avg_delivery_days,
                  avg_review_score
           from marts.mart_late_delivery_by_state
           where delivered_orders >= 200
           order by late_rate_pct desc""",
        "row",
        {"graph.dimensions": ["customer_state"], "graph.metrics": ["late_rate_pct"]},
    )
    cards["late_csat"] = create_card(
        db_id, "Review score: on-time vs late",
        """select case when is_late then 'Late' else 'On time' end as delivery,
                  round(avg(review_score)::numeric, 2) as avg_review,
                  count(*) as orders
           from marts.fct_orders
           where is_delivered and is_late is not null and review_score is not null
           group by 1
           order by 1 desc""",
        "bar",
        {"graph.dimensions": ["delivery"], "graph.metrics": ["avg_review"]},
    )

    # Dashboard
    status, dash = req("POST", "/api/dashboard", {
        "name": "Olist E-Commerce Performance",
        "description": "Revenue, average order value, category mix, delivery performance and customer repeat rate from the Olist public dataset (2016–2018).",
    })
    print("dashboard", status, dash.get("id") if isinstance(dash, dict) else dash)
    if status not in (200, 201):
        raise SystemExit(f"dashboard create failed: {dash}")
    dash_id = dash["id"]

    def card(cid, row, col, x, y):
        return {
            "id": -abs(hash((cid, row, col))) % 100000 - 1,
            "card_id": cid,
            "row": row,
            "col": col,
            "size_x": x,
            "size_y": y,
            "parameter_mappings": [],
            "visualization_settings": {},
        }

    dashcards = [
        card(cards["orders"], 0, 0, 4, 3),
        card(cards["gmv"], 0, 4, 4, 3),
        card(cards["aov"], 0, 8, 4, 3),
        card(cards["repeat"], 0, 12, 4, 3),
        card(cards["late"], 0, 16, 4, 3),
        card(cards["review"], 0, 20, 4, 3),
        card(cards["revenue"], 3, 0, 24, 8),
        card(cards["categories"], 11, 0, 12, 8),
        card(cards["delivery_review"], 11, 12, 12, 8),
        card(cards["late_state"], 19, 0, 12, 8),
        card(cards["late_csat"], 19, 12, 12, 8),
    ]
    # Metabase 0.52 grid is often 24 columns
    # 6 KPIs of size_x=4 = 24. Good.

    status, body = req("PUT", f"/api/dashboard/{dash_id}", {
        "name": "Olist E-Commerce Performance",
        "description": dash.get("description"),
        "dashcards": dashcards,
    })
    print("put dashboard", status, "cards", len(body.get("dashcards", [])) if isinstance(body, dict) else body)
    if status not in (200, 201):
        # try older API
        print("PUT failed, trying POST cards")
        for c in dashcards:
            s, b = req("POST", f"/api/dashboard/{dash_id}/cards", {
                "cardId": c["card_id"],
                "row": c["row"],
                "col": c["col"],
                "sizeX": c["size_x"],
                "sizeY": c["size_y"],
            })
            print("add card", c["card_id"], s)
    print(f"DASHBOARD_URL={BASE}/dashboard/{dash_id}")
    Path = __import__("pathlib").Path
    Path("/tmp/metabase_dashboard_id.txt").write_text(str(dash_id))
    return 0


if __name__ == "__main__":
    sys.exit(main())
