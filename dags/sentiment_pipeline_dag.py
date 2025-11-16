from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta
import os

# -------------------------------
# PATH SETUP
# -------------------------------
REPO_ROOT = os.getenv('SENTIMENT_REPO', os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
BACKEND = os.path.join(REPO_ROOT, 'backend')
DATABASE = os.path.join(REPO_ROOT, 'database')
FRONTEND = os.path.join(REPO_ROOT, 'frontend')

default_args = {
    'owner': 'sentiment_team',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='sentiment_analysis_pipeline',
    default_args=default_args,
    description='Generate daily sentiment reports and refresh dashboard',
    start_date=datetime(2025, 1, 1),
    schedule='@daily',
    catchup=False,
) as dag:

    # 1️⃣ Daily Report Task
    run_daily_report = BashOperator(
        task_id='run_daily_report',
        bash_command=f"cd {REPO_ROOT} && python3 {os.path.join(DATABASE, 'daily_report.py')}"
    )

    # 2️⃣ Dashboard refresh trigger
    refresh_dashboard = BashOperator(
        task_id='refresh_dashboard',
        bash_command=f"mkdir -p {os.path.join(REPO_ROOT, 'tmp')} && echo $(date) > {os.path.join(REPO_ROOT, 'tmp', 'dashboard_refresh.txt')}"
    )

    # DAG flow: daily report → dashboard refresh
    run_daily_report >> refresh_dashboard
