# Kubernetes Deployment Guide

This directory contains Kubernetes configuration files for deploying the open source data warehouse stack components.

## Components
1. **ClickHouse** - Database deployment configuration for the analytics warehouse.
2. **Airflow** - Workflow orchestration platform deployment configuration.
3. **Traefik** - Reverse proxy and load balancer for service ingress.

### Secrets
Contains secret management configuration and scripts.

## Prerequisites

- Kubernetes cluster (Scaleway Kapsule recommended)
- kubectl configured
- Helm v3.x installed
- Docker for building custom images

## Deployment Instructions

### 1. Configure kubectl for Scaleway

Get the kubeconfig file for the Scaleway cluster:

```bash
scw k8s kubeconfig get cluster-id="<insert_cluster_id>" > ~/.kube/scaleway-config
```

Configure kubectl to use the Scaleway config:

```bash
export KUBECONFIG=~/.kube/scaleway-config
```

**IMPORTANT**: always point the `KUBECONFIG` env var to the Scaleway kubeconfig file when using `kubectl` commands.
Otherwise, you will be working with the default kubeconfig file, which may not point to the Scaleway cluster.

Verify connection to the cluster:

```bash
kubectl get nodes
```

### 2. Create Secrets

See [README.md](secrets/README.md) for details:

```bash
sh ./k8s/secrets/create-secrets.sh <path-to-your-env-file> <environment>
```

### 3. Deploy ClickHouse

Install ClickHouse using Helm:

```bash
helm install clickhouse bitnami/clickhouse -n clickhouse -f k8s/clickhouse/values.yaml 
```

Wait for the ClickHouse deployment to be ready:

```bash
kubectl get pods -n clickhouse
```

#### Access ClickHouse

**Option 1: Using Traefik (For Web UI)**

If you have Traefik deployed (see [Deploy Traefik](#5-deploy-traefik-optional) section):

1. Port forward Traefik service:
```bash
kubectl port-forward -n default svc/traefik 8123:80
```

2. Access ClickHouse Web UI at `http://clickhouse.local:9000/play`.

**Option 2: Port Forwarding (For CLI Access)**

1. Port forward the ClickHouse service to your local machine:
```bash
# Port forward ClickHouse native protocol (for CLI)
kubectl port-forward svc/clickhouse 9000:9000 -n clickhouse
```

2. Check the ClickHouse service status by visiting the web UI at `http://localhost:9000`

This should return below message:
```text
Port 9000 is for clickhouse-client program
You must use port 8123 for HTTP.
```
We will use this clickhouse-client later to connect to the ClickHouse database.

### 4. Deploy Airflow

#### Build and Push the Airflow Docker Image

```bash
# Build and tag the Docker image
docker buildx build --platform linux/amd64 -t <your-registry-url>/weather-etl-dev/airflow-with-dags:latest . 

# Push the image to your registry
docker push <your-registry-url>/airflow-with-dags:latest
```

Note: Replace `<your-registry-url>` with your actual registry URL, e.g., `rg.fr-par.scw.cloud/weather-etl-dev`. Run `terraform output`.

#### Create Namespace for Airflow

```bash
kubectl create namespace airflow
```

#### Deploy Airflow with Helm

```bash
# Add the Airflow Helm repository
helm repo add apache-airflow https://airflow.apache.org

# Deploy Airflow using your custom image
helm install airflow apache-airflow/airflow \
  --namespace airflow \
  --values k8s/airflow/values.yaml \
  --version 1.17.0
```

#### Access Airflow UI

**Using Traefik**

If you have Traefik deployed (see [Deploy Traefik](#5-deploy-traefik-optional) section):

- Port forward Traefik service:
```bash
kubectl port-forward -n default svc/traefik 8123:80
```

- Access Airflow UI at `http://airflow.local:8123`.


#### Troubleshooting

Check Pod Status:
```bash
kubectl get pods -n airflow
```

View Pod Logs:
```bash
kubectl logs -f <pod-name> -n airflow
```

View events in the namespace:
```bash
kubectl get events -n airflow
```

### 5. Deploy Traefik

For local development access to services:

**Prerequisites**: Ensure ClickHouse and Airflow are deployed first, as the IngressRoutes reference these services.

#### Installation

1. Add the Traefik Helm repository:
```bash
helm repo add traefik https://traefik.github.io/charts
helm repo update
```

2. Install Traefik:
```bash
helm install traefik traefik/traefik -f k8s/traefik/values.yaml
```

3. Apply the IngressRoutes for your services (only after ClickHouse and Airflow are deployed):
```bash
kubectl apply -f k8s/traefik/ingressroutes.yaml
```

#### Access Services

**With Port Forwarding (Recommended for Development)**

1. Forward Traefik service to local port:
```bash
kubectl port-forward -n default svc/traefik 8123:80
```

2. Update /etc/hosts

Add these entries to your `/etc/hosts` file:
```
127.0.0.1 traefik.local
127.0.0.1 airflow.local
127.0.0.1 clickhouse.local
```

3. Access web UIs from your browser:
- Traefik Dashboard: `http://traefik.local:8123/dashboard/`
- Airflow: `http://airflow.local:8123`
- ClickHouse: `http://clickhouse.local:8123/play`

## Setup ClickHouse for Airflow

After all services are deployed, set up the ClickHouse database for Airflow usage:

### Install ClickHouse CLI

Install Clickhouse CLI - [DOCS](https://clickhouse.com/docs/install)

For macOS, you can use Homebrew:

```bash
brew install --cask clickhouse
```

### Connect to ClickHouse

```bash
clickhouse-client --host localhost --port 9000 --user default --password
```

> Note: Traefik only supports HTTP traffic, so CLI access requires direct port forwarding to the ClickHouse service (see [Access ClickHouse](#access-clickhouse) section).

### Create Airflow User and Database

1. Enter the password when prompted

2. Create the `airflow_dbt` user:

```sql
CREATE USER IF NOT EXISTS airflow_dbt IDENTIFIED WITH plaintext_password BY 'password123';
```

3. Create the `weather` database:

```sql
CREATE DATABASE IF NOT EXISTS weather;
```

4. Grant permissions to the `airflow_dbt` user on the `weather` database:

```sql
GRANT ALL ON weather.* TO airflow_dbt;
```

5. Grant S3 permissions to the `airflow_dbt` user:

```sql
GRANT S3 ON *.* TO airflow_dbt;
```

