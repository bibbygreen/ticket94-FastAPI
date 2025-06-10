# Terraform

This directory contains Terraform configurations to provision and manage Google Cloud infrastructure for the backend application.

## Resources Created

- **Cloud Run Service** (optional): A serverless container platform for deploying and scaling the backend application with CPU throttling when idle (only pay for requests)
- **Cloud SQL PostgreSQL Instance**: A managed PostgreSQL database for storing application data with both public and private IP access
- **VPC Network**: A private network with auto-created subnets for secure database access
- **Private Service Connection**: Enables private connectivity between your VPC and Google Cloud services
- **VPC Access Connector**: Allows Cloud Run to securely connect to resources in the VPC network
- **Cloud Storage Bucket**: A storage bucket for storing files and assets
- **Artifact Registry Repository**: A Docker repository for storing and managing container images
- **Service Account**: A dedicated service account for Cloud Run with appropriate permissions

## Prerequisites

- [Terraform](https://www.terraform.io/downloads.html) (v1.0 or later)
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
- A Google Cloud service account with appropriate permissions
- The service account key file (`xxxxxxxx.json`) in the parent directory

## Getting Started

1. **Initialize Terraform**:

   ```bash
   terraform init
   ```

2. **Configure Variables**:

   Copy the example variables file and modify as needed:

   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

   Edit `terraform.tfvars` to set your desired values, especially the database password.

3. **Plan the Deployment**:

   ```bash
   terraform plan -out=tfplan
   ```

   Review the plan to ensure it will create the resources you expect.

4. **Apply the Configuration**:

   ```bash
   terraform apply tfplan
   ```

   This will create all the resources defined in the configuration.

5. **Access Outputs**:

   After applying, Terraform will display output values. You can also retrieve them later:

   ```bash
   terraform output
   ```

   For sensitive outputs like passwords:

   ```bash
   terraform output database_password
   ```

## Updating Infrastructure

To update the infrastructure after making changes to the configuration:

1. Make your changes to the Terraform files
2. Run `terraform plan` to see what will change
3. Run `terraform apply` to apply the changes

## Destroying Infrastructure

To destroy all resources created by this configuration:

1. Set `deletion_protection = false` in the Cloud SQL instance resource in `main.tf`
2. Run `terraform apply` to update the instance
3. Run `terraform destroy` to destroy all resources

**Warning**: This will permanently delete all data in the database and storage bucket.

## Notes

- The Cloud SQL instance has deletion protection enabled by default. You must set `deletion_protection = false` and apply the change before you can destroy the instance.
- The storage bucket has versioning enabled and a lifecycle rule to move older objects to Nearline storage after 30 days.
- The Cloud Run service is configured with `cpu_idle = true`, which enables CPU throttling when the service is not processing requests. This implements the "only pay for requests" billing model, reducing costs when the service is idle.

## Configuration Options

### Cloud Run Deployment

You can choose whether to deploy the Cloud Run service by setting the `enable_cloud_run` variable:

```hcl
enable_cloud_run = true  # Set to false to disable Cloud Run deployment
```

When set to `false`, the Cloud Run service and related resources (VPC connector, service account, IAM permissions) will not be created. This is useful if you want to deploy only the infrastructure components (database, storage, etc.) and deploy the application separately.

## Application Environment Variables

The Cloud Run service (when enabled) requires several environment variables to function properly. These are defined in the Terraform configuration and should be set in your `terraform.tfvars` file:

### Core Settings
- `app_mode`: Application mode (dev, test, prod)
- `secret_key`: Secret key for JWT token generation
- `algorithm`: Algorithm for JWT token generation (default: HS256)
- `access_token_expire_minutes`: Expiration time for access tokens in minutes


### Database
- `database_url`: Automatically configured from the Cloud SQL instance using the format `postgresql+asyncpg://username:password@host:5432/database`


## VPC and Private Network Configuration

The infrastructure uses a VPC network with private connectivity to Cloud SQL:

- **VPC Network**: A Virtual Private Cloud network with auto-created subnets in each region
- **Private Service Connection**: Establishes a private connection between your VPC and Google Cloud services
- **Cloud SQL with Dual IP Configuration**:
  - **Private IP**: Accessible only from resources within the same VPC network
  - **Public IP**: Accessible from authorized IP addresses defined in `authorized_ip_ranges`

### Benefits of Private IP for Cloud SQL

1. **Enhanced Security**: Database traffic never traverses the public internet
2. **Simplified Network Security**: No need to manage SSL certificates or firewall rules
3. **Better Performance**: Lower latency for applications in the same VPC
4. **Compliance**: Helps meet regulatory requirements for data security

### Connecting to Cloud SQL

- **From within the VPC** (e.g., from GKE, GCE, Cloud Run):
  - Use the private IP address or private connection string
  - Example: `terraform output database_private_connection_string`

- **From outside the VPC**:
  - Use the public IP address with authorized networks
  - Configure `authorized_ip_ranges` in terraform.tfvars to restrict access
  - Example: `terraform output database_public_connection_string`

### Authorized Networks

You can restrict public access to specific IP addresses by configuring the `authorized_ip_ranges` variable:

```hcl
authorized_ip_ranges = {
  "office" = "203.0.113.0/24",  # Example office network
  "dev-machine" = "198.51.100.5/32"  # Single IP address
}
```
