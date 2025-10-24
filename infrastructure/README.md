# Banking Service Infrastructure as Code

This directory contains the Infrastructure as Code (IaC) for deploying the Banking Service on Azure using Terraform.

## Architecture Overview

The banking service is deployed on Azure using the following components:

- **Compute**: Azure Container Apps for serverless container deployment
- **Database**: Azure Database for PostgreSQL (Flexible Server) with encryption and SSL/TLS
- **Security**: Azure Key Vault for secrets management
- **Networking**: Azure Virtual Network with service endpoints
- **Monitoring**: Application Insights for logging and monitoring

## Prerequisites

1. **Terraform** >= 1.5.0
2. **Azure CLI** >= 2.50.0
3. **Azure Subscription** with appropriate permissions
4. **Environment Variables**:
   - `ARM_SUBSCRIPTION_ID`
   - `ARM_TENANT_ID`
   - `ARM_CLIENT_ID`
   - `ARM_CLIENT_SECRET`

## Deployment Steps

### 1. Initialize Terraform

```bash
cd infrastructure
terraform init
```

### 2. Plan Deployment

```bash
terraform plan -out=tfplan
```

### 3. Apply Configuration

```bash
terraform apply tfplan
```

### 4. Retrieve Outputs

```bash
terraform output
```

## Configuration Variables

Edit `terraform.tfvars` to customize deployment:

```hcl
environment = "production"
location = "eastus"
app_name = "banking-service"
database_version = "15"
container_port = 8000
replica_count = 2
```

## Security Features

- **Encryption at Rest**: Enabled for database and storage
- **Encryption in Transit**: TLS 1.2+ enforced
- **Network Security**: Virtual Network with service endpoints
- **Access Control**: Role-Based Access Control (RBAC)
- **Secrets Management**: Azure Key Vault integration
- **Audit Logging**: Application Insights monitoring
- **Password Policy**: Strong password requirements enforced

## Monitoring & Logging

- Application Insights for application monitoring
- Log Analytics Workspace for centralized logging
- Azure Monitor for infrastructure metrics
- Custom alerts for critical events

## Cost Optimization

- Auto-scaling based on CPU and memory
- Container Apps consumption-based pricing
- PostgreSQL flexible server with burstable SKU option
- Scheduled scaling for off-peak hours

## Terraform State Management

State is stored remotely in Azure Storage:

```bash
# Backend configuration in backend.tf
resource "azurerm_storage_account" "terraform" {
  # Configured separately
}
```

## Disaster Recovery

- Database backups: Daily automated backups retained for 30 days
- Geo-redundant storage for state files
- Multi-region capable with DNS failover
- Container image replicas in multiple regions

## Cleanup

```bash
terraform destroy
```

## Support

For issues or questions, refer to:
- [Azure Provider Documentation](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Terraform Documentation](https://www.terraform.io/docs)
