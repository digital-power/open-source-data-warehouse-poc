#!/bin/bash

# Script to create Kubernetes secrets for weather ETL system from .env file
# Usage: ./create-secrets.sh [path-to-env-file] [environment]

ENV_FILE=${1:-"../../.env"}
ENVIRONMENT=${2:-dev}

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: .env file not found at $ENV_FILE"
    echo "Usage: $0 [path-to-env-file] [environment]"
    exit 1
fi

echo "Creating Kubernetes secrets from $ENV_FILE for environment: $ENVIRONMENT"

# Source the .env file to load variables
set -a  # automatically export all variables
source "$ENV_FILE"
set +a  # turn off automatic export

# Create namespaces if they don't exist
kubectl create namespace airflow --dry-run=client -o yaml | kubectl apply -f -
kubectl create namespace clickhouse --dry-run=client -o yaml | kubectl apply -f -

echo "Creating secrets using environment variables..."

# Generate consistent passwords for this deployment
PG_PASSWORD="airflow-postgres-$(openssl rand -hex 8)"
ADMIN_PASSWORD="admin-$(openssl rand -hex 6)"
WEBSERVER_SECRET="airflow-webserver-$(openssl rand -hex 16)"

# Airflow database secrets (using generated values for database passwords)
kubectl create secret generic airflow-secrets \
  --namespace=airflow \
  --from-literal=postgres-password="$PG_PASSWORD" \
  --from-literal=metadb-password="$PG_PASSWORD" \
  --from-literal=webserver-secret-key="$WEBSERVER_SECRET" \
  --from-literal=admin-password="$ADMIN_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f -

# External API secrets from .env file
kubectl create secret generic external-api-secrets \
  --namespace=airflow \
  --from-literal=geocoding-api-key="$GEOCODING_API_KEY" \
  --from-literal=scaleway-access-key="$SCW_ACCESS_KEY" \
  --from-literal=scaleway-secret-key="$SCW_SECRET_KEY" \
  --from-literal=s3-access-key="$S3_ACCESS_KEY" \
  --from-literal=s3-secret-key="$S3_SECRET_KEY" \
  --dry-run=client -o yaml | kubectl apply -f -


# ClickHouse connection secrets from .env file - for Airflow
kubectl create secret generic clickhouse-connection-secret \
  --namespace=airflow \
  --from-literal=clickhouse-password="$CLICKHOUSE_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f -

# ClickHouse database secrets from .env file - for ClickHouse
kubectl create secret generic clickhouse-secrets \
  --namespace=clickhouse \
  --from-literal=clickhouse-password="$CLICKHOUSE_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f -

echo ""
echo "✅ Secrets created successfully from .env file!"
echo ""
echo "Generated passwords:"
echo "- PostgreSQL password: $PG_PASSWORD"
echo "- Admin password: $ADMIN_PASSWORD"
echo ""
echo "Created secrets:"
echo "- airflow-secrets (postgres, webserver, admin passwords)"  
echo "- external-api-secrets (API keys from .env)"
echo "- clickhouse-connection-secret (ClickHouse password from .env)"
echo "- clickhouse-secrets (ClickHouse password from .env)"
echo ""
echo "Note: airflow-postgresql and airflow-metadata secrets will be created by Helm"
echo ""
echo "To verify secrets were created:"
echo "kubectl get secrets -n airflow"
echo "kubectl get secrets -n clickhouse"
echo ""
echo "To view secret values (base64 encoded):"
echo "kubectl get secret external-api-secrets -n airflow -o yaml"