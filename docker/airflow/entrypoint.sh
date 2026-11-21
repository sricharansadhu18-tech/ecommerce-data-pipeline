#!/usr/bin/env bash
set -euo pipefail

echo "[ecommerce] waiting for Postgres..."
python - <<'PY'
import os, time
import psycopg2
for i in range(60):
    try:
        conn = psycopg2.connect(
            host=os.environ.get("PGHOST", "postgres"),
            port=os.environ.get("PGPORT", "5432"),
            user=os.environ.get("PGUSER", "ecommerce"),
            password=os.environ.get("PGPASSWORD", "ecommerce"),
            dbname="airflow",
        )
        conn.close()
        print("[ecommerce] Postgres is ready")
        break
    except Exception as exc:
        print(f"[ecommerce] Postgres not ready ({exc}); retrying...")
        time.sleep(2)
else:
    raise SystemExit("Postgres did not become ready in time")
PY

echo "[ecommerce] migrating Airflow metadata database..."
airflow db migrate

echo "[ecommerce] ensuring admin user exists..."
airflow users create \
    --username "${AIRFLOW_ADMIN_USER:-admin}" \
    --firstname Sri \
    --lastname Charan \
    --role Admin \
    --email admin@localhost.local \
    --password "${AIRFLOW_ADMIN_PASSWORD:-admin}" \
    || true

echo "[ecommerce] starting scheduler in background..."
airflow scheduler &
SCHED_PID=$!

cleanup() {
    echo "[ecommerce] shutting down..."
    kill "${SCHED_PID}" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "[ecommerce] starting webserver on 8080..."
exec airflow webserver --port 8080
