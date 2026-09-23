import requests
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
import time
import os

APP_ID = os.environ["ADZUNA_APP_ID"]
APP_KEY = os.environ["ADZUNA_APP_KEY"]


def build_url(page: int) -> str:
    return (
        f"https://api.adzuna.com/v1/api/jobs/sg/search/{page}"
        f"?app_id={APP_ID}&app_key={APP_KEY}"
        f"&results_per_page=50&salary_min=1000&full_time=1&permanent=1"
)

def fetch_page(page: int) -> dict:

    for attempt in range(3):  # retry up to 3 times on bad response
        time.sleep(0.3) 
        response = requests.get(build_url(page))
        if response.status_code == 200 and response.text.strip():
            try:
                data = response.json()
                return data
            except ValueError:
                pass
        time.sleep(2 ** attempt)

    raise RuntimeError(f"Page {page} failed after 3 attempts")

def extract_adzuna():

    all_results =[]
    engine = create_engine("postgresql+psycopg2://airflow:airflow@postgres:5432/airflow")

    data=fetch_page(1)
    total_count = data["count"]
    total_pages = -(-total_count // 50)

    for page_number in range  (1,total_pages+1):

        data = fetch_page(page_number)
        results=data.get("results",[])
        all_results.extend(results)
        print(f"Page {page_number}/{total_pages} — total so far: {len(all_results)}")

        time.sleep(0.3)

    df = pd.DataFrame(all_results)


    df["extracted_at"] = datetime.now()
    
    dtype_map = {}

    for col in df.select_dtypes(include="object").columns:
    
        #get columns without null values
        sample = df[col].dropna()

        #select non-empty & dict and list vlue
        if not sample.empty and isinstance(sample.iloc[0], (dict, list)):

            #create a dictionary with the column , key set to JSONB
            dtype_map[col] = JSONB

    df.to_sql("adzuna_jobs", engine ,if_exists= "append", index=False,dtype=dtype_map)