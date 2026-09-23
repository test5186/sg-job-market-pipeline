import time
from datetime import datetime

import pandas as pd
import requests
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB

URL = "https://api.mycareersfuture.gov.sg/v2/jobs"

def last_page() -> int:


    for attempt in range(3):
        response = requests.get(URL)
        if response.status_code == 200 and response.text.strip():
            try:
                data = response.json()
                break
            except ValueError:
                pass
        time.sleep(2 ** attempt)  # backoff: 1s, 2s, 4s
    else:
        raise RuntimeError("Failed to fetch last_page after retries")
    
    # response = requests.get(URL)
    # data = response.json()
    href = data["_links"]["last"]["href"]
    end_page = href.split("page=")[1].split("&")[0]

    #insurance +50 incase changes while processing
    return int(end_page) + 50
    


def sg(chunk_index:int, num_chunks: int, ti=None):
    total_page = ti.xcom_pull(task_ids="last_page")

    #Chunk size is how many each task need to process
    chunk_size = (total_page//num_chunks) + 1
    start_page = chunk_index * chunk_size
    end_page = min(start_page + chunk_size,total_page)

    engine = create_engine("postgresql+psycopg2://airflow:airflow@postgres:5432/airflow")

    for page in range (start_page,end_page):

        params = {
            "limit":20,
            "page":page,
            "salary":0
        }

        for attempt in range(3):  # retry up to 3 times on bad response
            time.sleep(0.3) 
            response = requests.get(URL, params=params)
            if response.status_code == 200 and response.text.strip():
                try:
                    data = response.json()
                    break
                except ValueError:
                    pass
            time.sleep((attempt + 1) * 10 * 60)  # 10min, 20min, 30min
        else:
            print(f"[chunk {chunk_index}] page {page} failed after retries, skipping")
            continue

        # response = requests.get(URL, params=params)
        # data=response.json()

        result = data.get("results",[])

        #Empty list would result in TRUE
        if not result:
            break

        df = pd.DataFrame(data["results"])

        # Add extraction timestamp
        df["extracted_at"] = datetime.now()

        dtype_map = {}

        #Check if value is a list or dict

        #select columns with object types
        for col in df.select_dtypes(include="object").columns:

            #get columns without null values
            sample = df[col].dropna()

            #select non-empty & dict and list vlue
            if not sample.empty and isinstance(sample.iloc[0], (dict, list)):

                #create a dictionary with the column , key set to JSONB
                dtype_map[col] = JSONB

        df.to_sql("raw_jobs", engine ,if_exists= "append", index=False,dtype=dtype_map)

        print(f"[chunk {chunk_index}] done page {page}")

        time.sleep(1.0)
