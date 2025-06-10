# Terraform Configuration for FastAPI Deployment

This Terraform configuration allows you to deploy a FastAPI application using Docker Compose to a remote server via SSH.

## Prerequisites

- [Terraform](https://www.terraform.io/downloads.html) >= 1.0
- SSH access to a remote server
- Docker and Docker Compose installed on the remote server


## Configuration

1. Copy `terraform.tfvars.example` to `terraform.tfvars`:

```bash
cp terraform.tfvars.example terraform.tfvars
```

2. Edit `terraform.tfvars` to set your configuration values:

```hcl
# SSH deployment configuration
ssh_host = "your-server-ip"
ssh_user = "your-ssh-username"
ssh_private_key_path = "~/.ssh/id_rsa"  # Path to your private key file
ssh_port = 22
remote_dir = "/path/to/remote/directory"
docker_compose_file = "../docker-compose.yml"
env_file = "../env/.env.remote"
db_env_file = "../env/.env.db"
```

## Usage

Initialize Terraform:

```bash
terraform init
```

Plan the deployment:

```bash
terraform plan
```

Apply the configuration:

```bash
terraform apply
```

To destroy the deployed resources:

```bash
terraform destroy
```

## Files

- `main.tf`: Main Terraform configuration file
- `variables.tf`: Variable definitions
- `terraform.tfvars`: Variable values (not committed to version control)
- `terraform.tfvars.example`: Example variable values

## Notes

- The `terraform.tfvars` file contains sensitive information and should not be committed to version control.
- This configuration uses the `null_resource` provider to execute SSH commands on the remote server.
- The deployment is triggered when the Docker Compose file or environment files change.
