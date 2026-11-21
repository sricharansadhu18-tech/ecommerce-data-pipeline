FROM apache/airflow:2.10.4-python3.12

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev git \
    && rm -rf /var/lib/apt/lists/*

USER airflow
# Pin dbt-core to the 1.10 line so pip does not pull a pre-release.
RUN pip install --no-cache-dir "dbt-core>=1.10.0,<1.11" "dbt-postgres==1.10.2"

COPY --chown=airflow:0 src /opt/ecommerce/src
COPY --chown=airflow:0 dbt /opt/ecommerce/dbt
COPY --chown=airflow:0 data /opt/ecommerce/data
COPY --chown=airflow:0 airflow/dags /opt/airflow/dags
COPY --chown=airflow:0 docker/airflow/entrypoint.sh /entrypoint-ecommerce.sh

USER root
RUN chmod +x /entrypoint-ecommerce.sh
USER airflow

WORKDIR /opt/airflow
ENTRYPOINT ["/entrypoint-ecommerce.sh"]
