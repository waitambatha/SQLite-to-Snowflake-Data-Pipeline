from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
import pandas as pd
import sqlite3
import os
from datetime import datetime

# Snowflake connection ID (MUST match Airflow connection ID)
SNOWFLAKE_CONN_ID = "snowflake_ab"

# Define paths
SQLITE_DB_PATH = "/opt/airflow/dags/data_source.db"
CSV_FILE_PATH = "/tmp/sqlite_data.csv"

# Snowflake table name
SNOWFLAKE_TABLE = "customers"


def extract_sqlite_data(**kwargs):
    """Extracts data from SQLite and saves it as CSV."""
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        df = pd.read_sql("SELECT * FROM customers;", conn)
        df.to_csv(CSV_FILE_PATH, index=False)
        conn.close()
        print(f"Data extracted to {CSV_FILE_PATH}")
    except Exception as e:
        print(f"Extraction failed: {e}")
        raise


def load_to_snowflake(**kwargs):
    """Loads CSV data into Snowflake."""
    try:
        hook = SnowflakeHook(snowflake_conn_id=SNOWFLAKE_CONN_ID)

        # PUT and COPY commands
        sql = f"""
        PUT file://{CSV_FILE_PATH} @%{SNOWFLAKE_TABLE};
        COPY INTO {SNOWFLAKE_TABLE}
        FROM @%{SNOWFLAKE_TABLE}/{os.path.basename(CSV_FILE_PATH)}
        FILE_FORMAT = (TYPE = CSV SKIP_HEADER = 1);
        """

        hook.run(sql)
        os.remove(CSV_FILE_PATH)
        print("Data loaded successfully!")
    except Exception as e:
        print(f"Loading failed: {e}")
        raise


# DAG configuration
default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 2, 11),
    "retries": 1,
}

with DAG(
        "sqlite_to_snowflake_final",
        default_args=default_args,
        schedule_interval="@daily",
        catchup=False,
) as dag:
    extract = PythonOperator(
        task_id="extract_sqlite_data",
        python_callable=extract_sqlite_data,
    )

    load = PythonOperator(
        task_id="load_data_to_snowflake",
        python_callable=load_to_snowflake,
    )

    extract >> load