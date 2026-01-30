This directory contains the workflow implementation using Apache Airflow as the primary orchestrator. These DAGs (Directed Acyclic Graphs) serve as the Python-based equivalents to Kestra's YAML flows, providing a more programmatic approach to data pipeline management.📋 Project StructurePlaintext021-workflow-orchestration/


├── dags/                    # Airflow DAG definitions
│   ├── 07_gcp_setup.py      # Initial GCP setup (Bucket & Dataset)
│   ├── 08_gcp_taxi.py       # Manual taxi data processing
│   └── 09_gcp_taxi_scheduled.py  # Scheduled taxi data processing
├── logs/                    # Local Airflow execution logs
├── plugins/                 # Custom Airflow operators/hooks
├── config/                  # Environment configuration
├── gcp_keys/                # GCP Service Account keys (GIT IGNORED)
├── docker-compose.yml       # Container orchestration
├── Dockerfile               # Custom Airflow image with dependencies
├── requirements.txt         # Python library dependencies
├── .env                     # Environment variables (create manually)
└── README.md                # Project documentation

 Initial Setup
 
 1. Configure Environment Variables
 
 Create a .env file in the project root to manage your environment-specific settings:
 

 
 # Airflow Config

AIRFLOW_UID=50000
AIRFLOW_PROJ_DIR=./

# GCP Configuration
GCP_PROJECT_ID=your-project-id
GCP_DATASET=your_dataset_name
GCP_BUCKET_NAME=your_unique_bucket_name
GCP_LOCATION=us-central1
GCP_CREDENTIALS_FILE=my-creds.json

# Airflow Web UI Credentials
_AIRFLOW_WWW_USER_USERNAME=airflow
_AIRFLOW_WWW_USER_PASSWORD=airflow

2. GCP Credentials
Download your Service Account JSON key from the GCP Console.

Place it in the gcp_keys/ folder.Name it according to your .env file (e.g., my-creds.json).

3. Initialize & StartBash

# Set UID for permissions
export AIRFLOW_UID=$(id -u)

# Initialize the Airflow Database

docker-compose up airflow-init

# Start all services in the background
docker-compose up -d

# Available DAGs
1. 07_gcp_setupGoal: Infrastructure as Code (simplified).Tasks: Creates the required GCS Bucket and BigQuery Dataset.Execution: Run once before starting the data pipelines.
2. 08_gcp_taxi (Manual)Goal: On-demand data ingestion from GitHub to BigQuery.Trigger: Manual with JSON configuration.JSON Example:JSON{ "taxi": "yellow", "year": "2021", "month": "01" }
3. 09_gcp_taxi_scheduledGoal: Regular data updates.Schedule: * Green Taxi: 1st of every month at 09:00 AM.Yellow Taxi: 1st of every month at 10:00 AM.


