# FastAPI-Template

A production-ready FastAPI template with built-in authentication, database integration, containerization, and infrastructure as code. This template provides a solid foundation for building scalable and maintainable API services with Python.

## Features

- **FastAPI Framework**: High-performance, easy-to-use web framework
- **SQLAlchemy ORM**: Database integration with migration support via Alembic
- **Authentication**: Built-in JWT authentication system
- **Docker Support**: Containerization for consistent development and deployment
- **Infrastructure as Code**: Terraform configurations for various deployment scenarios
- **CI/CD Pipeline**: GitLab CI/CD configuration
- **Environment Management**: Structured environment variable management
- **Testing**: Pytest configuration for API testing
- **Code Quality**: Pre-commit hooks for code quality enforcement

## Prerequisites

- Python 3.12+
- Poetry (Python dependency management)
- Docker and Docker Compose (for containerized development)
- Terraform (for infrastructure provisioning)
- Make (for running convenience commands)

## Project Structure

```
fastapi-template/
├── alembic/                  # Database migration scripts
├── ansible/                  # Ansible deployment configurations
├── env.example/              # Example environment variable files
├── scripts/                  # Utility scripts
├── src/                      # Application source code
│   ├── auth/                 # Authentication module
│   ├── database/             # Database module
│   ├── main.py               # Main entry point
│   └── models/               # Database models
├── terraform/                # Infrastructure as code configurations
│   ├── dev_deploy/           # Development deployment
│   ├── gcp_compute_engine/   # GCP Compute Engine configuration
│   ├── gcp_db_bucket_repository/ # GCP database and storage
│   ├── gcp_vm_deploy/        # GCP VM deployment
│   └── prod/                 # Production environment
└── tests/                    # Test suite
```

## Local Development Environment

### 1. Clone the Repository

```bash
git clone <repository-url>
cd fastapi-template
```

### 2. Set Up Environment Variables

```bash
# Create env directory if it doesn't exist
mkdir -p env

# Copy environment files
cp env.example/.env.example env/.env
cp env.example/.env.db.example env/.env.db
cp env.example/.env.remote.example env/.env.remote
```

Edit the environment files with your configuration:
- `env/.env` - Local environment variables (API settings, logging, etc.)
- `env/.env.db` - Database configuration (connection string, credentials)
- `env/.env.remote` - Remote deployment settings (used for staging)

### 3. Set Up Python Environment

```bash
# Create and activate virtual environment
poetry shell

# Install dependencies
poetry install
```

### 4. Install Pre-commit Hooks

```bash
pre-commit install
```

### 5. Set Up Database with Terraform

```bash
# Navigate to the appropriate Terraform directory
cd terraform/dev_deploy

# Copy and configure Terraform variables
cp terraform.tfvars.example terraform.tfvars

# Initialize Terraform
terraform init

# Review infrastructure plan
terraform plan

# Apply infrastructure to set up the remote database
terraform apply

# Return to project root
cd ../..
```

### 6. Run the Application

```bash
make run
```

### 7. Access API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc


## Set Up Development Environment with Terraform

### 1. Set Up Environment Files

```bash
# Copy and configure environment files if not done already
cp env.example/.env.example env/.env
cp env.example/.env.db.example env/.env.db
cp env.example/.env.remote.example env/.env.remote
```

### 2. Navigate to Terraform Dev Environment Directory

```bash
cd terraform/dev_deploy
```

### 3. Copy and Configure Terraform Variables

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your specific configuration values.

### 4. Set Up Docker Compose

Review and edit `docker-compose.yml` with your configuration if needed.

### 5. Initialize and Apply Terraform

```bash
# Initialize Terraform
terraform init

# Review infrastructure plan
terraform plan

# Apply infrastructure
terraform apply
```

## Testing

Run the test suite with:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src
```

## Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

## Makefile Commands

The project includes several convenience commands in the Makefile:

```bash
# Run the application
make run

# Run tests
make test

# Run linting
make lint

# Generate a new migration
make generate_migration

# Apply database migrations
make migrate
```
