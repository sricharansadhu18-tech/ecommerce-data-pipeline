#!/usr/bin/env python3
"""Capture Metabase, dbt docs lineage and Airflow DAG screenshots."""

from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parents[1] / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)
WIDTH, HEIGHT, SCALE = 1600, 900, 2

MB_EMAIL = "sri.charan@localhost.local"
MB_PASS = "EcommerceAnalytics1!"
AF_USER = "admin"
AF_PASS = "admin"


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="/usr/bin/google-chrome",
            headless=True,
            args=["--no-sandbox", "--disable-gpu", "--hide-scrollbars"],
        )
        page = browser.new_page(
            viewport={"width": WIDTH, "height": HEIGHT},
            device_scale_factor=SCALE,
        )

        # ---- Metabase ----
        page.goto("http://127.0.0.1:3000/auth/login", wait_until="networkidle")
        page.wait_for_timeout(800)
        # already logged in? if we see dashboard skip
        if page.locator("input[type='email'], input[name='username']").count():
            page.fill("input[type='email'], input[name='username']", MB_EMAIL)
            page.fill("input[type='password']", MB_PASS)
            page.click("button[type='submit']")
            page.wait_for_timeout(2000)
        page.goto("http://127.0.0.1:3000/dashboard/2", wait_until="networkidle")
        page.wait_for_timeout(6000)  # let cards query
        # hide any popovers/toasts
        page.keyboard.press("Escape")
        page.wait_for_timeout(500)
        mb = OUT / "metabase-dashboard.png"
        page.screenshot(path=str(mb), full_page=True)
        print(f"wrote {mb} ({mb.stat().st_size/1024:.0f} KB)")
        # also a viewport hero
        hero = OUT / "metabase-dashboard-hero.png"
        page.screenshot(path=str(hero), full_page=False)
        print(f"wrote {hero} ({hero.stat().st_size/1024:.0f} KB)")

        # ---- dbt docs lineage ----
        # overview first
        page.goto("http://127.0.0.1:8081/#!/overview", wait_until="networkidle")
        page.wait_for_timeout(2000)
        # try the project lineage graph
        page.goto(
            "http://127.0.0.1:8081/#!/graph/model.olist_ecommerce.fct_orders",
            wait_until="networkidle",
        )
        page.wait_for_timeout(3000)
        # if graph canvas exists, good; otherwise open model page and click lineage
        if page.locator("svg, canvas, .graph, #graph").count() == 0:
            page.goto(
                "http://127.0.0.1:8081/#!/model/model.olist_ecommerce.fct_orders",
                wait_until="networkidle",
            )
            page.wait_for_timeout(2000)
            for sel in [
                "button[title*='ineage' i]",
                "text=Lineage",
                ".launcher-graph",
                "[data-testid='graph']",
                "a[href*='graph']",
            ]:
                loc = page.locator(sel)
                if loc.count():
                    loc.first.click()
                    page.wait_for_timeout(2500)
                    break
        lineage = OUT / "dbt-lineage.png"
        page.screenshot(path=str(lineage), full_page=False)
        print(f"wrote {lineage} ({lineage.stat().st_size/1024:.0f} KB)")
        # also overview
        page.goto("http://127.0.0.1:8081/#!/overview", wait_until="networkidle")
        page.wait_for_timeout(1500)
        ov = OUT / "dbt-docs-overview.png"
        page.screenshot(path=str(ov), full_page=False)
        print(f"wrote {ov} ({ov.stat().st_size/1024:.0f} KB)")

        # ---- Airflow ----
        page.goto("http://127.0.0.1:8080/login/", wait_until="networkidle")
        page.wait_for_timeout(800)
        if page.locator("input#username, input[name='username']").count():
            page.fill("input#username, input[name='username']", AF_USER)
            page.fill("input#password, input[name='password']", AF_PASS)
            page.click("button[type='submit'], input[type='submit']")
            page.wait_for_timeout(2000)
        # Graph view
        for url in [
            "http://127.0.0.1:8080/dags/ecommerce_analytics_pipeline/grid?tab=graph",
            "http://127.0.0.1:8080/dags/ecommerce_analytics_pipeline/graph",
            "http://127.0.0.1:8080/graph?dag_id=ecommerce_analytics_pipeline",
        ]:
            page.goto(url, wait_until="networkidle")
            page.wait_for_timeout(2500)
            if "login" not in page.url:
                break
        # try to dismiss banners
        page.keyboard.press("Escape")
        page.wait_for_timeout(500)
        af = OUT / "airflow-dag-run.png"
        page.screenshot(path=str(af), full_page=False)
        print(f"wrote {af} page={page.url} ({af.stat().st_size/1024:.0f} KB)")
        # also grid of runs
        page.goto(
            "http://127.0.0.1:8080/dags/ecommerce_analytics_pipeline/grid",
            wait_until="networkidle",
        )
        page.wait_for_timeout(2000)
        grid = OUT / "airflow-grid.png"
        page.screenshot(path=str(grid), full_page=False)
        print(f"wrote {grid} ({grid.stat().st_size/1024:.0f} KB)")

        browser.close()


if __name__ == "__main__":
    main()
