from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash_operator import BashOperator

from momo.helper.file_helper import FileHelper

with DAG(
    "echo_dag",
    default_args={
      'owner': "Dataplatform Momo",
      'email': "dataplatform_momo@mservice.com.vn",
      'depends_on_past': False,
      'start_date': datetime(2020, 7, 14, 0, 0, 0),
      'retries': 2,
      'retry_delay': timedelta(minutes=5)
    },
    schedule_interval=None,
    catchup=False,
    max_active_runs=1,
    concurrency=1,
    description="Echo DAG help to echo text when triggered"
) as dag:

  echo_something = BashOperator(
      task_id='echo_something',
      bash_command='echo Momo has a weird Data Platform')

  sql = FileHelper.read_file(path="/usr/local/airflow/cfg/code/some.sql")

  sql_something = BashOperator(
      task_id='sql_something',
      bash_command=f'sql "{sql}""')

  echo_something >> sql_something