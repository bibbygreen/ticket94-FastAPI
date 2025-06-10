# Network outputs
output "vpc_network_name" {
  description = "The name of the VPC network"
  value       = google_compute_network.vpc_network.name
}

output "vpc_network_id" {
  description = "The ID of the VPC network"
  value       = google_compute_network.vpc_network.id
}

# Database outputs
output "database_instance_name" {
  description = "The name of the database instance"
  value       = google_sql_database_instance.postgres_instance.name
}

output "database_instance_connection_name" {
  description = "The connection name of the database instance"
  value       = google_sql_database_instance.postgres_instance.connection_name
}

output "database_instance_public_ip_address" {
  description = "The public IP address of the database instance"
  value       = google_sql_database_instance.postgres_instance.public_ip_address
}

output "database_instance_private_ip_address" {
  description = "The private IP address of the database instance"
  value       = google_sql_database_instance.postgres_instance.private_ip_address
}

output "database_name" {
  description = "The name of the database"
  value       = google_sql_database.database.name
}

output "database_user" {
  description = "The database user"
  value       = google_sql_user.user.name
}

output "database_password" {
  description = "The database password (only shown if auto-generated)"
  value       = google_sql_user.user.password
  sensitive   = true
}

output "database_public_connection_string" {
  description = "The public connection string for the database"
  value       = "postgresql://${google_sql_user.user.name}:${google_sql_user.user.password}@${google_sql_database_instance.postgres_instance.public_ip_address}:5432/${google_sql_database.database.name}"
  sensitive   = true
}

output "database_private_connection_string" {
  description = "The private connection string for the database (for use within the VPC)"
  value       = "postgresql://${google_sql_user.user.name}:${google_sql_user.user.password}@${google_sql_database_instance.postgres_instance.private_ip_address}:5432/${google_sql_database.database.name}"
  sensitive   = true
}

# Storage outputs
output "storage_bucket_name" {
  description = "The name of the storage bucket"
  value       = google_storage_bucket.storage_bucket.name
}

output "storage_bucket_url" {
  description = "The URL of the storage bucket"
  value       = google_storage_bucket.storage_bucket.url
}

output "storage_bucket_self_link" {
  description = "The self link of the storage bucket"
  value       = google_storage_bucket.storage_bucket.self_link
}

# Redis outputs
output "redis_instance_name" {
  description = "The name of the Redis instance"
  value       = google_redis_instance.redis_instance.name
}

output "redis_instance_host" {
  description = "The hostname or IP address of the Redis instance"
  value       = google_redis_instance.redis_instance.host
}

output "redis_instance_port" {
  description = "The port of the Redis instance"
  value       = google_redis_instance.redis_instance.port
}

output "redis_instance_connection_string" {
  description = "The connection string for the Redis instance"
  value       = "${google_redis_instance.redis_instance.host}:${google_redis_instance.redis_instance.port}"
}

# Artifact Registry outputs
output "artifact_registry_repository_name" {
  description = "The name of the Artifact Registry repository"
  value       = google_artifact_registry_repository.project_repo.name
}

output "artifact_registry_repository_id" {
  description = "The ID of the Artifact Registry repository"
  value       = google_artifact_registry_repository.project_repo.id
}

output "artifact_registry_repository_location" {
  description = "The location of the Artifact Registry repository"
  value       = google_artifact_registry_repository.project_repo.location
}

output "artifact_registry_docker_repository_url" {
  description = "The URL to use for Docker repository"
  value       = "${google_artifact_registry_repository.project_repo.location}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.project_repo.repository_id}"
}

# Cloud Run outputs
output "cloud_run_service_name" {
  description = "The name of the Cloud Run service"
  value       = var.enable_cloud_run ? google_cloud_run_v2_service.backend-app[0].name : "Cloud Run not enabled"
}

output "cloud_run_service_url" {
  description = "The URL of the Cloud Run service"
  value       = var.enable_cloud_run ? google_cloud_run_v2_service.backend-app[0].uri : "Cloud Run not enabled"
}

output "cloud_run_service_status" {
  description = "The status of the Cloud Run service"
  value       = var.enable_cloud_run ? google_cloud_run_v2_service.backend-app[0].latest_created_revision : "Cloud Run not enabled"
}

output "vpc_connector_name" {
  description = "The name of the VPC connector"
  value       = var.enable_cloud_run ? google_vpc_access_connector.connector[0].name : "VPC connector not created (Cloud Run not enabled)"
}

output "cloud_run_service_account_email" {
  description = "The email of the service account used by Cloud Run"
  value       = var.enable_cloud_run ? google_service_account.cloud_run_service_account[0].email : "Service account not created (Cloud Run not enabled)"
}
