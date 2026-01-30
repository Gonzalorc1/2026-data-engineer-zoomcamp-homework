from datetime import datetime
from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateEmptyDatasetOperator
from airflow.providers.google.cloud.operators.gcs import GCSCreateBucketOperator
import os

# GCP configuration variables
# Note: Ensure these Env Vars are set in your environment or Docker setup
GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'your-gcp-project-id')
GCP_DATASET = os.getenv('GCP_DATASET', 'taxi_dataset')
GCP_BUCKET_NAME = os.getenv('GCP_BUCKET_NAME', 'your-bucket-name')
GCP_LOCATION = os.getenv('GCP_LOCATION', 'US') # GCS locations are often better as 'US' or 'EU'

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
}

with DAG(
    '07_gcp_setup',
    default_args=default_args,
    description='Configure GCP resources (Bucket and Dataset)',
    schedule_interval=None, 
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['gcp', 'setup'],
) as dag:

    # FIX: Removed project_id (handled by the connection)
    create_gcs_bucket = GCSCreateBucketOperator(
        task_id='create_gcs_bucket',
        bucket_name=GCP_BUCKET_NAME,
        location=GCP_LOCATION,
        storage_class='STANDARD',
        gcp_conn_id='google_cloud_default' # Ensure this exists in Airflow Connections
    )

    create_bq_dataset = BigQueryCreateEmptyDatasetOperator(
        task_id='create_bq_dataset',
        dataset_id=GCP_DATASET,
        project_id=GCP_PROJECT_ID,
        location=GCP_LOCATION,
        exists_ok=True, # Modern version of 'if_exists'
    )

    create_gcs_bucket >> create_bq_dataset