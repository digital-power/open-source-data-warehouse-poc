import os

# Constants for the data pipeline ingestion module
GEOCODING_API_KEY = os.environ.get("GEOCODING_API_KEY", "")
GEOCODING_API_URL = "https://api.api-ninjas.com/v1/geocoding"
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"

CLICKHOUSE_HOST = os.environ.get("CLICKHOUSE_HOST", "clickhouse.clickhouse.svc.cluster.local")
CLICKHOUSE_PORT = int(os.environ.get("CLICKHOUSE_PORT", "8123"))
CLICKHOUSE_USER = os.environ.get("CLICKHOUSE_USER", "airflow_dbt")
CLICKHOUSE_PASSWORD = os.environ.get("CLICKHOUSE_PASSWORD", "password123")
CLICKHOUSE_DATABASE = os.environ.get("CLICKHOUSE_DATABASE", "default")

# Scaleway Object Storage configuration from environment variables
SCALEWAY_ACCESS_KEY = os.environ.get("SCALEWAY_ACCESS_KEY", "")
SCALEWAY_SECRET_KEY = os.environ.get("SCALEWAY_SECRET_KEY", "")
SCALEWAY_ENDPOINT_URL = "https://weather-data-dev.s3.fr-par.scw.cloud"
SCALEWAY_BUCKET = "weather-data-dev"