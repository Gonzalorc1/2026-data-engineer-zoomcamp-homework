import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import io

# Data URLs
parquet_url = "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-11.parquet"
csv_url = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv"

# PostgreSQL configuration
db_config = {
    'host': 'localhost',
    'port': 5433,
    'database': 'ny_taxi',
    'user': 'postgres',
    'password': 'postgres'
}

# Create SQLAlchemy connection
engine = create_engine(f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}")

print("Downloading and reading zones data...")
# Read zones CSV directly from URL
df_zones = pd.read_csv(csv_url)
print(f"Zones loaded: {len(df_zones)} rows")

print("Downloading and reading trips data...")
# Read Parquet directly from URL
df_trips = pd.read_parquet(parquet_url)
print(f"Trips loaded: {len(df_trips)} rows")

# Create zones table
print("\nCreating zones table...")
df_zones.to_sql(name='zones', con=engine, if_exists='replace', index=False)
print("Table 'zones' created and inserted successfully")

# Create trips table
print("\nCreating trips table...")
df_trips.to_sql(name='green_taxi_trips', con=engine, if_exists='replace', index=False)
print("Table 'green_taxi_trips' created and inserted successfully")

print("\nIngestion completed successfully!")
