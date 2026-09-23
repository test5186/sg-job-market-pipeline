# SG Job Market ELT Pipeline

An automated pipeline that extracts job postings from Singapore's MyCareersFuture and Adzuna APIs, loads them into Postgres, and transforms them with dbt into a deduplicated, queryable dataset — orchestrated end-to-end with Apache Airflow.

## What it does

- **Extracts** job listings from two sources in parallel:
  - **MyCareersFuture** (Singapore government job portal) — paginated via 50 concurrent Airflow tasks
  - **Adzuna** — public job search API
- **Loads** raw JSON responses into Postgres, preserving nested fields as JSONB
- **Transforms** with dbt through a staging → intermediate → mart layered architecture:
  - Parses and flattens JSONB fields (skills, categories, salary, employer)
  - Deduplicates each source independently, then merges both into one combined dataset — matching on normalized company + title to catch cross-platform duplicates
  - Filters and aggregates into a final mart layer (e.g. skill-tally for "data engineer" roles)
- **Validates** the pipeline automatically with dbt tests (`unique`, `not_null`, `accepted_values`, plus a custom test asserting the dedup logic actually holds)
- **Runs on every push** via GitHub Actions CI: Python linting (`ruff`) and dbt project validation (`dbt parse`)

## Architecture

```
                    ┌─────────────────┐
                    │   last_page      │
                    └────────┬─────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                              ▼
   ┌──────────────────────┐      ┌────────────────────┐
   │ chunk_task_0..49      │      │  extract_adzuna     │
   │ (MyCareersFuture,     │      │  (paginated,        │
   │  50 parallel tasks)   │      │   retry + backoff)  │
   └──────────┬────────────┘      └──────────┬──────────┘
              │                              │
              └──────────────┬───────────────┘
                              ▼
                     ┌─────────────────┐
                     │    dbt_build     │
                     │ (dbt build:      │
                     │  run + test)     │
                     └─────────────────┘
```

All extraction runs in parallel; `dbt_build` waits for every upstream task to succeed before running `dbt build` — which runs the full model chain and every data test in one pass.

## Setup

**Prerequisites**: Docker, Docker Compose, an [Adzuna API key](https://developer.adzuna.com/).

```bash
git clone https://github.com/test5186/sg-job-market-pipeline.git
cd sg-job-market-pipeline

cp .env.example .env
# then edit .env with your own Adzuna credentials

docker compose build
docker compose up -d
```

Airflow UI: `http://localhost:8080`

Trigger the pipeline manually, or via CLI:
```bash
docker compose exec airflow-scheduler airflow dags trigger extract
```

## Project structure

```
dags/extract.py              # Airflow DAG: extraction + dbt build
include/sg.py                # MyCareersFuture extraction logic
include/sg_adzuna.py         # Adzuna extraction logic (paginated, retry/backoff)
dbt/jobs_dbt/models/
  staging/                    # parse raw JSONB per source
  intermediate/                # dedup per source, then combine
  mart/                        # filtered, aggregated outputs
dbt/jobs_dbt/tests/           # custom data test (dedup integrity)
.github/workflows/ci.yml      # lint + dbt parse on every push
```

## Status

This is an active learning/portfolio project. Current scope is Singapore job data only; the architecture (particularly the Adzuna extractor) is built to extend to additional country markets with minimal changes.
