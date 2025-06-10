# VPC Network with auto-created subnets
resource "google_compute_network" "vpc_network" {
  name                    = "${var.project_id}-vpc"
  auto_create_subnetworks = true
  description             = "VPC Network for ${var.project_id}"
}

# Private Service Connection
resource "google_compute_global_address" "private_ip_address" {
  name          = "${var.project_id}-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc_network.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.vpc_network.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
}

# Cloud SQL PostgreSQL Instance
resource "google_sql_database_instance" "postgres_instance" {
  name             = "${var.project_id}-db-instance"
  database_version = "POSTGRES_17"
  region           = var.region
  depends_on       = [google_service_networking_connection.private_vpc_connection]

  settings {
    tier              = "db-f1-micro"  # Smallest instance, adjust as needed
    availability_type = "ZONAL"        # REGIONAL or ZONAL
    disk_size         = 10
    disk_type         = "PD_SSD"
    edition           = "ENTERPRISE"

    backup_configuration {
      enabled            = true
      start_time         = "03:00"
    }
    
    ip_configuration {
      ipv4_enabled    = true
      private_network = google_compute_network.vpc_network.id
      
      dynamic "authorized_networks" {
        for_each = var.authorized_ip_ranges
        content {
          name  = authorized_networks.key
          value = authorized_networks.value
        }
      }
    }
    
    database_flags {
      name  = "max_connections"
      value = "250"
    }
  }
  
  deletion_protection = false
}

# PostgreSQL Database
resource "google_sql_database" "database" {
  name     = var.database_name
  instance = google_sql_database_instance.postgres_instance.name
  charset  = "UTF8"
  collation = "en_US.UTF8"
}

# Database User
resource "google_sql_user" "user" {
  name     = var.database_user
  instance = google_sql_database_instance.postgres_instance.name
  password = var.database_password
  
  depends_on = [
    google_sql_database.database
  ]
}

# Cloud Storage Bucket
resource "google_storage_bucket" "storage_bucket" {
  name          = "${var.storage_bucket_name}-${var.project_id}"
  location      = var.storage_location
  storage_class = var.storage_class
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = 30  # days
    }
    action {
      type = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }
  
  # Optional: Configure CORS if needed
  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD", "PUT", "POST", "DELETE"]
    response_header = ["*"]
    max_age_seconds = 3600
  }
}

# Redis Instance (Memorystore for Redis)
resource "google_redis_instance" "redis_instance" {
  name           = "${var.project_id}-redis"
  tier           = var.redis_tier
  memory_size_gb = var.redis_memory_size_gb
  region         = var.region
  
  authorized_network = google_compute_network.vpc_network.id
  connect_mode       = "PRIVATE_SERVICE_ACCESS"
  
  redis_version     = var.redis_version
  display_name      = "Redis Cache"
  
  depends_on = [
    google_service_networking_connection.private_vpc_connection
  ]
  
  maintenance_policy {
    weekly_maintenance_window {
      day = "SUNDAY"
      start_time {
        hours   = 2
        minutes = 0
      }
    }
  }
  
  redis_configs = {
    "maxmemory-policy" = "allkeys-lru"
  }
}

# Artifact Registry Repository
resource "google_artifact_registry_repository" "project_repo" {
  location      = var.region
  repository_id = "${var.project_id}"
  description   = "Docker repository for ${var.project_id}"
  format        = "DOCKER"

  docker_config {
    immutable_tags = false
  }

  cleanup_policies {
    id     = "keep-minimum-versions"
    action = "KEEP"
    condition {
      tag_state    = "TAGGED"
      tag_prefixes = ["v"]
      newer_than   = "2592000s" # 30 days
    }
  }

  cleanup_policies {
    id     = "delete-old-untagged"
    action = "DELETE"
    condition {
      tag_state  = "UNTAGGED"
      older_than = "2592000s" # 30 days
    }
  }
}

# Cloud Run Service
resource "google_cloud_run_v2_service" "backend-app" {
  count    = var.enable_cloud_run ? 1 : 0
  name     = var.cloud_run_service_name
  location = var.region
  deletion_protection = false
  ingress = "INGRESS_TRAFFIC_ALL"
  invoker_iam_disabled = false
  
  template {
    containers {
      image = var.cloud_run_container_image
      
      ports {
        container_port = var.cloud_run_container_port
      }
      
      resources {
        limits = {
          cpu    = var.cloud_run_cpu
          memory = var.cloud_run_memory
        }
        cpu_idle = true
      }
      
      # Environment variables for the container
      env {
        name  = "DATABASE_URL"
        value = "postgresql+asyncpg://${google_sql_user.user.name}:${var.database_password}@${google_sql_database_instance.postgres_instance.private_ip_address}:5432/${google_sql_database.database.name}"
      }
      
      env {
        name  = "REDIS_HOST"
        value = google_redis_instance.redis_instance.host
      }
      
      env {
        name  = "REDIS_PORT"
        value = google_redis_instance.redis_instance.port
      }
      
      env {
        name  = "REDIS_PASSWORD"
        value = var.redis_password
      }
      
      env {
        name  = "STORAGE_BUCKET"
        value = google_storage_bucket.storage_bucket.name
      }
      
      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }
      
      env {
        name  = "MODE"
        value = var.app_mode
      }
      
      env {
        name  = "SECRET_KEY"
        value = var.secret_key
      }
      
      env {
        name  = "ALGORITHM"
        value = var.algorithm
      }
      
      env {
        name  = "ACCESS_TOKEN_EXPIRE_MINUTES"
        value = var.access_token_expire_minutes
      }      
    }
    
    scaling {
      min_instance_count = var.cloud_run_min_instances
      max_instance_count = var.cloud_run_max_instances
    }
    
    timeout = "${var.cloud_run_timeout_seconds}s"
    
    max_instance_request_concurrency = var.cloud_run_concurrency
    
    # Connect to the VPC
    vpc_access {
      connector = google_vpc_access_connector.connector[0].id
      egress = "PRIVATE_RANGES_ONLY"
    }
  }

  # Depend on the VPC connector
  depends_on = [
    google_vpc_access_connector.connector,
    google_sql_database_instance.postgres_instance,
    google_redis_instance.redis_instance,
    google_storage_bucket.storage_bucket
  ]
}

# VPC Access Connector for Cloud Run to connect to VPC
resource "google_vpc_access_connector" "connector" {
  count         = var.enable_cloud_run ? 1 : 0
  name          = "${var.project_id}-vpc-connector"
  region        = var.region
  network       = google_compute_network.vpc_network.name
  ip_cidr_range = "10.8.0.0/28"  # Specify a /28 CIDR range for the connector
  
  # Minimum and maximum instances for the connector
  min_instances = 2
  max_instances = 3
  
  # Depend on the VPC network
  depends_on = [
    google_compute_network.vpc_network
  ]
}

# IAM policy to make the Cloud Run service publicly accessible
resource "google_cloud_run_service_iam_member" "public_access" {
  count    = var.enable_cloud_run ? 1 : 0
  location = google_cloud_run_v2_service.backend-app[0].location
  service  = google_cloud_run_v2_service.backend-app[0].name
  role     = "roles/run.invoker"
  member   = "allUsers"  # Public access - change to specific users/groups for restricted access
  
  depends_on = [
    google_cloud_run_v2_service.backend-app
  ]
}

# Service account for Cloud Run to access other GCP resources
resource "google_service_account" "cloud_run_service_account" {
  count       = var.enable_cloud_run ? 1 : 0
  account_id   = "${var.project_id}-run-sa"
  display_name = "Service Account for Cloud Run"
}

# Grant the service account access to Cloud SQL
resource "google_project_iam_member" "cloud_run_sql_access" {
  count   = var.enable_cloud_run ? 1 : 0
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.cloud_run_service_account[0].email}"
}

# Grant the service account access to Cloud Storage
resource "google_storage_bucket_iam_member" "cloud_run_storage_access" {
  count  = var.enable_cloud_run ? 1 : 0
  bucket = google_storage_bucket.storage_bucket.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.cloud_run_service_account[0].email}"
}

# Grant the service account access to Redis
resource "google_project_iam_member" "cloud_run_redis_access" {
  count   = var.enable_cloud_run ? 1 : 0
  project = var.project_id
  role    = "roles/redis.admin"
  member  = "serviceAccount:${google_service_account.cloud_run_service_account[0].email}"
}
