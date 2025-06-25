# Kubernetes Secrets Management

This directory contains scripts and documentation for managing Kubernetes secrets in the weather ETL system.

## Quick Start

1. **Ensure you have a .env file with required variables** (see Environment Variables section)

2. **Create secrets from your .env file:**
   ```bash
   cd k8s/secrets
   ./create-secrets.sh <path-to-your-env-file> <environment>
   ```

## Environment Variables Required

Your `.env` file must contain these variables:

```bash
# API Keys
GEOCODING_API_KEY=your_geocoding_api_key_here

# Scaleway/S3 Configuration  
SCW_ACCESS_KEY=your_scaleway_access_key
SCW_SECRET_KEY=your_scaleway_secret_key
S3_ACCESS_KEY=your_s3_access_key  
S3_SECRET_KEY=your_s3_secret_key

# ClickHouse Configuration
CLICKHOUSE_PASSWORD=your_clickhouse_password
```

## Secret Structure

### Airflow Namespace
- `airflow-secrets`: Auto-generated database and web server credentials
  - `postgres-password` (auto-generated)
  - `metadb-password` (auto-generated) 
  - `webserver-secret-key` (auto-generated)
  - `admin-password` (auto-generated)
- `external-api-secrets`: Third-party API keys from .env
  - `geocoding-api-key` (from GEOCODING_API_KEY)
  - `scaleway-access-key` (from SCW_ACCESS_KEY)
  - `scaleway-secret-key` (from SCW_SECRET_KEY)
  - `s3-access-key` (from S3_ACCESS_KEY)
  - `s3-secret-key` (from S3_SECRET_KEY)
- `clickhouse-connection-secret`: ClickHouse connection from .env
  - `clickhouse-password` (from CLICKHOUSE_PASSWORD)

### ClickHouse Namespace
- `clickhouse-secrets`: ClickHouse database password from .env
  - `clickhouse-password` (from CLICKHOUSE_PASSWORD)

## How the Script Works

The `create-secrets.sh` script:
1. ✅ Sources your `.env` file to load environment variables
2. ✅ Creates Kubernetes namespaces (airflow, clickhouse) 
3. ✅ Generates secure random passwords for Airflow internal components
4. ✅ Uses your actual API credentials from `.env` for external services
5. ✅ Creates all secrets with proper naming and namespacing

## Managing Secrets

### Update Existing Secret
```bash
kubectl patch secret external-api-secrets -n airflow \
  --type='merge' \
  -p='{"data":{"scaleway-access-key":"<new-base64-value>"}}'
```

### View Secret (base64 encoded)
```bash
kubectl get secret external-api-secrets -n airflow -o yaml
```

### Decode Secret Value
```bash
kubectl get secret external-api-secrets -n airflow -o jsonpath='{.data.geocoding-api-key}' | base64 -d
```

### List All Secrets
```bash
kubectl get secrets -n airflow
kubectl get secrets -n clickhouse
```

## Security Best Practices

1. **Never commit .env files to version control** - Add `.env` to `.gitignore`
2. **Use separate .env files per environment** (`.env.dev`, `.env.prod`)
3. **Rotate secrets regularly**
4. **Use RBAC to limit secret access**
5. **Consider using external secret management** (AWS Secrets Manager, HashiCorp Vault)

## Environment-Specific Deployments

For different environments, create separate .env files:

```bash
# Development
./create-secrets.sh .env.dev

# Production  
./create-secrets.sh .env.prod
```

## Troubleshooting

### Script Can't Find .env File
- Ensure `.env` file exists in project root
- Use absolute path: `./create-secrets.sh /full/path/to/.env`

### Missing Environment Variables
- Check your `.env` file contains all required variables
- Variables must not have spaces around `=`
- Quote values with special characters

### Pod Can't Access Secret
- Verify secret exists: `kubectl get secrets -n <namespace>`
- Check secret name and key in Helm values
- Verify namespace matches between secret and deployment

### Secret Values Not Working
- Decode and verify secret contents
- Check for extra whitespace or encoding issues
- Recreate secret if values are corrupted