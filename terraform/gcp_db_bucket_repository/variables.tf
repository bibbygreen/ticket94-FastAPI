variable "project_id" {
  description = "The ID of the Google Cloud project"
  type        = string
  default     = ""
}

variable "region" {
  description = "The region to deploy resources to"
  type        = string
  default     = "asia-east1"  # Taiwan region
}

variable "zone" {
  description = "The zone to deploy resources to"
  type        = string
  default     = "asia-east1-b"
}

variable "database_name" {
  description = "The name of the database to create"
  type        = string
  default     = "postgres_instance"
}

variable "database_user" {
  description = "The username for the database"
  type        = string
  default     = "db_user"
}

variable "database_password" {
  description = "The password for the database user"
  type        = string
  sensitive   = true
  default     = "SimplePassword123"  # Default simple password for development
}

variable "storage_bucket_name" {
  description = "The name of the storage bucket to create"
  type        = string
  default     = "storage-bucket"
}

variable "storage_class" {
  description = "The storage class of the bucket"
  type        = string
  default     = "STANDARD"
}

variable "storage_location" {
  description = "The location of the bucket"
  type        = string
  default     = "ASIA"
}

variable "authorized_ip_ranges" {
  description = "Map of authorized IP ranges that can access the Cloud SQL instance"
  type        = map(string)
  default     = {
    "office" = "0.0.0.0/0"  # Allow all IPs for dev, restrict for production
  }
}

# Cloud Run variables
variable "enable_cloud_run" {
  description = "Whether to enable Cloud Run service deployment"
  type        = bool
  default     = true
}

variable "cloud_run_service_name" {
  description = "The name of the Cloud Run service"
  type        = string
  default     = "backend-app"
}

variable "cloud_run_container_image" {
  description = "The container image to deploy to Cloud Run"
  type        = string
  default     = null # Should be provided via environment variable or tfvars file
}

variable "cloud_run_container_port" {
  description = "The port the container listens on"
  type        = number
  default     = 8000
}

variable "cloud_run_min_instances" {
  description = "Minimum number of instances for the Cloud Run service"
  type        = number
  default     = 0
}

variable "cloud_run_max_instances" {
  description = "Maximum number of instances for the Cloud Run service"
  type        = number
  default     = 2
}

variable "cloud_run_cpu" {
  description = "CPU allocation for Cloud Run instances (e.g., '1' or '2')"
  type        = string
  default     = "1"
}

variable "cloud_run_memory" {
  description = "Memory allocation for Cloud Run instances (e.g., '512Mi', '1Gi')"
  type        = string
  default     = "512Mi"
}

variable "cloud_run_timeout_seconds" {
  description = "Maximum request timeout in seconds (1-3600)"
  type        = number
  default     = 300
}

variable "cloud_run_concurrency" {
  description = "Maximum concurrent requests per instance"
  type        = number
  default     = 80
}

# Application environment variables
variable "app_mode" {
  description = "The application mode (dev, test, prod)"
  type        = string
  default     = "dev"
}

variable "secret_key" {
  description = "Secret key for JWT token generation"
  type        = string
  sensitive   = true
  default     = null
}

variable "algorithm" {
  description = "Algorithm for JWT token generation"
  type        = string
  default     = "HS256"
}

variable "access_token_expire_minutes" {
  description = "Expiration time for access tokens in minutes"
  type        = number
  default     = 60
}
