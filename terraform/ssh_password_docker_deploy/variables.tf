# SSH deployment variables
variable "remote_dir" {
  description = "Remote directory path to deploy docker-compose"
  type        = string
  default     = "/tmp"
}

variable "env_file" {
  description = "Path to the environment file"
  type        = string
}

variable "db_env_file" {
  description = "Path to the db environment file"
  type        = string
}

variable "ssh_host" {
  description = "Remote server IP address"
  type        = string
}

variable "ssh_user" {
  description = "SSH username"
  type        = string
}

variable "ssh_password" {
  description = "SSH password"
  type        = string
  sensitive   = true
}

variable "ssh_port" {
  description = "SSH port number"
  type        = number
  default     = 22
}

variable "docker_compose_file" {
  description = "Path to docker-compose.yml"
  type        = string
}
