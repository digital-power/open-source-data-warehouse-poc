# Terraform Infrastructure

This directory contains Terraform configuration files for deploying the infrastructure on Scaleway.

## Prerequisites

- Scaleway CLI installed and configured
- Terraform installed
- kubectl installed
- Helm v3.x installed
- Docker installed

## Infrastructure Setup

### 1. Initialize Terraform

```bash
cd terraform
terraform init
```

### 2. Configure Variables

Make sure you supply the required variables in a `terraform.tfvars` file or through `variables.tf`

### 3. Deploy Infrastructure

```bash
terraform apply
```

### 4. Get Cluster Information

Get the Kubernetes cluster ID from the Terraform output:

```bash
terraform output -raw cluster_id
```

This cluster ID will be used in the Kubernetes deployment steps. See the [K8s README](../k8s/README.md) for deployment instructions.

## Scaleway Services

The Terraform configuration provisions the following Scaleway services:

- **Kubernetes Kapsule**: Container orchestration platform
- **Object Storage**: Data storage for the data pipeline
- **Container Registry**: For storing custom Docker images
- **Secrets Manager**: For managing sensitive configuration (recommended for production)

## Outputs

After successful deployment, Terraform will output:

- `cluster_id`: Kubernetes cluster identifier
- `registry_url`: Container registry URL for pushing images
- `bucket_name`: Object storage bucket name
- Other relevant infrastructure details

## Cleanup

To destroy the infrastructure:

```bash
terraform destroy
```

**Warning**: This will permanently delete all resources. Make sure to backup any important data before running this command.