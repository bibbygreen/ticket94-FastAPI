variable "credentials_file" {
  description = "The path to the Google Cloud service account key file"
  type        = string
  default     = "../../service-key.json"
}

variable "project_id" {
  description = "The ID of the Google Cloud project"
  type        = string
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

variable "instance_name" {
  description = "The name of the compute instance"
  type        = string
  default     = "app-server"
}

variable "machine_type" {
  description = "The machine type of the compute instance"
  type        = string
  default     = "e2-micro"  # 2 vCPU, 1 GB memory (cheapest option)
}

variable "boot_disk_size" {
  description = "The size of the boot disk in GB"
  type        = number
  default     = 20
}

variable "boot_disk_type" {
  description = "The type of the boot disk"
  type        = string
}

variable "boot_disk_image" {
  description = "The image to use for the boot disk"
  type        = string
}

variable "network_tags" {
  description = "Network tags to apply to the instance"
  type        = list(string)
  default     = ["http-server", "https-server", "ssh", "backend-server"]
}

variable "ssh_username" {
  description = "The username for SSH access"
  type        = string
  default     = "ubuntu"
}

variable "ssh_pub_key_file" {
  description = "The path to the public SSH key file. Can be a default path with tilde (~/.ssh/id_rsa.pub), an absolute path (/Users/username/.ssh/id_rsa.pub), or a relative path to a local copy (./ssh_key.pub)"
  type        = string
}

variable "allow_stopping_for_update" {
  description = "If true, allows Terraform to stop the instance to update its properties"
  type        = bool
  default     = true
}

variable "enable_backend" {
  description = "If true, creates a firewall rule to allow traffic to backend ports"
  type        = bool
  default     = true
}

variable "backend_ports" {
  description = "List of ports to open for backend services"
  type        = list(number)
  default     = [8000, 8080]
}

variable "labels" {
  description = "A map of labels to apply to the instance"
  type        = map(string)
  default     = {}
}

variable "service_account_scopes" {
  description = "The scopes for the service account"
  type        = list(string)
  default = [
    "https://www.googleapis.com/auth/cloud-platform"
  ]
}

variable "metadata" {
  description = "Metadata key/value pairs to make available from within the instance"
  type        = map(string)
  default     = {}
}
