from airflow.decorators import dag
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from pendulum import datetime, duration

from include.sg import last_page, sg
from include.sg_adzuna import extract_adzuna

# Job listings split across NUM_CHUNKS parallel scrape tasks (for sg.py)
NUM_CHUNKS = 50

@dag(
    start_date = datetime(2025,1,1),
    schedule = None,
    catchup = False,
    description = "Extraction",
    tags = ["Extraction"],
    default_args = {
        "retries":1,
        },
    dagrun_timeout = duration(minutes=600),
    max_consecutive_failed_dag_runs = 2,
    max_active_runs = 1,
)

def extract():

    get_last_page = PythonOperator (
        task_id = 'last_page',
        python_callable = last_page
        )

    # Collect every chunk task so all 50 can be wired to dbt_build at once
    chunk_tasks = []
    for i in range (NUM_CHUNKS):
        chunk_task = PythonOperator (
            task_id = f'chunk_task_{i}',
            python_callable = sg,
            op_kwargs={"chunk_index": i, "num_chunks": NUM_CHUNKS},
            pool = 'scrape_pool'
        )

        get_last_page>>chunk_task
        chunk_tasks.append(chunk_task)

    get_adzuna = PythonOperator (
        task_id = 'extract_adzuna',
        python_callable = extract_adzuna
        )

    dbt_build = BashOperator(
        task_id='dbt_build',
        bash_command='cd /opt/airflow/dbt/jobs_dbt && dbt build --profiles-dir .'
    )

    #All success rule (default), dbt build wait till both have been extracted
    chunk_tasks >> dbt_build
    get_adzuna >> dbt_build

extract()