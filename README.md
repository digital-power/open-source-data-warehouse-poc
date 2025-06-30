# Open source data warehouse 

This project is intended to implement a data pipeline as POC on an open source data warehouse stack. 
It serves as and alternative to the popular Big Tech Cloud Data Warehouses like Databricks, Snowflake, or BigQuery.

It uses the following open source components:

- Apache Airflow for orchestration
- ClickHouse for warehousing 
- dbt for data transformation

The project is designed to be deployed on [Scaleway](https://www.scaleway.com/en/) European Cloud infrastructure using Kubernetes and Terraform.

It uses the following Scaleway services:
- Kubernetes for container orchestration
- Object Storage for data storage
- Secrets Manager for managing sensitive information

## Architecture Overview

![Architecture Overview](images/architecture.png)

## Data Pipeline
The data pipeline example collects weather forecast data from a public API, processes it, and stores it in ClickHouse for further analysis. 

### Ingestion
The pipeline consists of the following components:
- **Weather Data Collector**: Python service that fetches weather forecasts from a public API
- **Ingestion Layer**: Classes that handle data extraction and loading into S3 storage
- **Storage Client**: Manages interaction with Scaleway Object Storage for raw data persistence
- **ClickHouse Client**: Handles connections and data writing to ClickHouse
- **Airflow DAG**: Orchestrates the entire pipeline with scheduled execution

The `src/` directory contains all Python source code for the data pipeline:

- `data_pipeline/`: Root package for all pipeline components
  - `ingestion/`: Data ingestion services
    - `weather_data_collector.py`: Core module for retrieving weather forecasts
    - `clients/`: API clients for external services
      - `weather.py`: Client for the weather forecast API
      - `storage.py`: Client for S3-compatible object storage
      - `clickhouse.py`: Client for ClickHouse database operations
      - `base.py`: Base client classes and interfaces
    - `models/`: Data models for pipeline entities
      - `location.py`: Represents geographical locations for weather data
      - `scaleway_storage.py`: Models for interacting with cloud storage
      - `clickhouse.py`: Data structures for ClickHouse integration
    - `configs/`: Configuration settings and constants
    - `data/`: Static data files (e.g., dutch_cities.txt)
    - `utils/`: Helper functions and utilities

The pipeline uses Airflow for orchestration, with DAGs defined in the `dags/` directory. Weather data is first collected and stored as raw JSON in Scaleway Object Storage before being processed and loaded into ClickHouse using the dbt models described in the next section.

### Transformation
The project uses dbt (data build tool) to transform raw weather data into structured, analytics-ready datasets following a layered approach:

#### Raw Layer
- **raw_weather**: Ingests JSON weather data directly from S3 storage, preserving the raw content and adding a load timestamp. This model uses ClickHouse's native S3 functions to read data from the object storage bucket.

#### Staging Layer
- **stg_weather**: Transforms raw JSON data into a structured format by extracting specific weather attributes such as temperature, precipitation, and wind speed. This incremental model processes only new data since the last run, extracts city information, coordinates, and hourly weather metrics.

#### Mart Layer
- **mart_daily_weather_summary**: Provides aggregated daily weather statistics by city. This model calculates min/max/avg temperatures, wind speeds, and precipitation totals to support analytics use cases.

The models are optimized for ClickHouse, using appropriate materialization strategies and engine configurations for performance.

## Project Structure

- `dags/`: Airflow DAGs for weather data collection
- `dbt/`: Data transformation models using dbt
- `k8s/`: Kubernetes configuration for deployment
- `src/`: Python source code for the data pipeline
- `terraform/`: Infrastructure as code for Scaleway setup

## Local Development

### Prerequisites

- Python 3.11 or later
- Docker and Docker Compose
- UV package manager

### Setup

Clone the repository:

```bash
git clone <repository-url>
cd open-source-data-warehouse-poc
```

## Deployment 
For deployment of the open source warehouse, we will use Scaleway's infrastructure with Kubernetes and Terraform.

## Scaleway

### Prerequisites

- Scaleway CLI installed and configured
- Terraform installed
- kubectl installed
- Helm v3.x installed
- Docker installed

### Infrastructure Setup

1. Initialize Terraform:

```bash
cd terraform
terraform init
```

2. Run Terraform:

Make sure you supply the required variables in a `terraform.tfvars` file or through `variables.tf`

```bash
terraform apply
```

3. Get the Kubernetes cluster ID from the Terraform output:

```bash
terraform output -raw cluster_id
```

### Configure kubectl for Scaleway

4. Get the kubeconfig file for the Scaleway cluster:

```bash
scw k8s kubeconfig get cluster-id="<insert_cluster_id>" > ~/.kube/scaleway-config
```

5. Configure kubectl to use the Scaleway config:

```bash
export KUBECONFIG=~/.kube/scaleway-config
```

IMPORTANT: always point the `KUBECONFIG` env var to the Scaleway kubeconfig file when using `kubectl` commands.
Otherwise, you will be working with the default kubeconfig file, which may not point to the Scaleway cluster.

6. Verify connection to the cluster:

```bash
kubectl get nodes
```

7. Create secrets - see [README.md](k8s/secrets/README.md) for details:

```bash
cd ../k8s/secrets
./create-secrets.sh <path-to-your-env-file> <environment>
```

### Deploy ClickHouse

8. Install ClickHouse using Helm:

```bash
helm install clickhouse bitnami/clickhouse -n clickhouse -f k8s/clickhouse/values.yaml 
```

9. Wait for the ClickHouse deployment to be ready:

```bash
kubectl get pods -n clickhouse
```

10. Forward the ClickHouse port to access it locally - programmatically or via CLI:

```bash
kubectl port-forward svc/clickhouse 9000:9000 -n clickhouse
kubectl port-forward svc/clickhouse 8123:8123 -n clickhouse
```

Via the browser, you can access the ClickHouse web UI at `http://localhost:8123/play`.

#### Airflow User

1. Install Clickhouse CLI - [DOCS](https://clickhouse.com/docs/install)

For macOS, you can use Homebrew:

```bash
brew install --cask clickhouse
```

2. Connect to ClickHouse:

```bash
clickhouse-client --host localhost --port 9000 --user default --password
```

3. Enter the password when prompted


4. Create the `airflow_dbt` user and grant permissions:

```sql
CREATE USER IF NOT EXISTS airflow_dbt IDENTIFIED WITH plaintext_password BY 'password123';
```

#### Grant Permissions
1. Create the `weather` database:

```sql
CREATE DATABASE IF NOT EXISTS weather;
```

2. Grant permissions to the `airflow_dbt` user on the `weather` database:

```sql
GRANT ALL ON weather.* TO airflow_dbt;
```

3. Grant S3 permissions to the `airflow_dbt` user:

```sql
GRANT S3 ON *.* TO airflow_dbt;
```

### Deploy Airflow

#### 1. Build and Push the Airflow Docker Image

```bash
# Build the Docker image
docker build -t airflow-with-dags:latest .  
# Or use buildx for multi-platform support
docker buildx build --platform linux/amd64 -t rg.fr-par.scw.cloud/weather-etl-dev/airflow-with-dags:latest . 

# Tag the image for your registry
docker tag airflow-with-dags:latest <your-registry-url>/airflow-with-dags:latest

# Push the image to your registry
docker push <your-registry-url>/airflow-with-dags:latest
```

Note: Replace `<your-registry-url>` with your actual registry URL, e.g., `rg.fr-par.scw.cloud/weather-etl-dev`. Run `terraform output`.

#### 3. Create Namespace for Airflow

```bash
kubectl create namespace airflow
```

#### 4. Deploy Airflow with Helm

```bash
# Add the Airflow Helm repository
helm repo add apache-airflow https://airflow.apache.org

# Deploy Airflow using your custom image
helm install airflow apache-airflow/airflow \
  --namespace airflow \
  --values k8s/airflow/values.yaml \
  --version 1.17.0
```

#### 5. Access Airflow UI

**Using Port Forwarding**

```bash
kubectl port-forward svc/airflow-api-server 8080:8080 -n airflow
```

Access the Airflow UI at http://localhost:8080 (default credentials: admin/admin)

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

## Running the Pipeline

The weather data collection pipeline runs on a schedule defined in the Airflow DAG. You can also trigger it manually from the Airflow UI.

## Data Transformation

dbt models are used for transforming the raw weather data into useful analytics tables. To run the dbt models:

```bash
cd dbt
dbt run
```

## To do's

1. General improvements
- [ ] Separate infrastructure, k8s manifests, ingestion and transformation code into different repositories.
- [ ] Re-evaluate secret management strategy, possibly using an external secrets manager with [helm secrets plugin](https://github.com/jkroepke/helm-secrets).  
- [ ] Add more comprehensive documentation for each component.

1. Airflow improvements
- [ ] Check production guidelines - [Airflow Production Guidelines](https://airflow.apache.org/docs/helm-chart/stable/production-guide.html).
- [ ] Use managed Postgres as Airflow metastore.
- [ ] Sync dags from Git repo instead of building them into the Docker image.
- [ ] Store logs in Scaleway Object Storage.
- [ ] Add Postgres as metadata database for Airflow.
- [ ] Add Redis for caching and task queue.

1. ClickHouse improvements
- [ ] Add ClickHouse 3rd party interface for better user experience - [options](https://clickhouse.com/docs/interfaces/third-party)

1. Additional components
- [ ] Add ArgoCD for continuous deployment and monitoring of deployments.
- [ ] Add unity catalog for data lineage and governance.

1. Networking
- [ ] Add Ingress or Load Balancer for external access to Airflow and ClickHouse.