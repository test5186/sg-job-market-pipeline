FROM apache/airflow:2.10.5

RUN pip install dbt-core==1.11.11 dbt-postgres==1.10.0

