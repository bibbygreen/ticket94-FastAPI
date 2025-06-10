terraform {
  required_version = ">= 1.0"
  
  required_providers {
    null = {
      source  = "hashicorp/null"
      version = "~> 3.0"
    }
  }
}

# SSH Docker deployment resource
resource "null_resource" "deploy" {
  connection {
    type     = "ssh"
    user     = var.ssh_user
    password = var.ssh_password
    host     = var.ssh_host
    port     = var.ssh_port
  }

  # Trigger conditions to check if docker-compose.yml and .env files have changed
  triggers = {
    docker_compose_md5 = filemd5(var.docker_compose_file)
    env_file_md5       = filemd5(var.env_file)
    db_env_file_md5    = filemd5(var.db_env_file)
  }

  # Create specified directories
  provisioner "remote-exec" {
    inline = [
      "mkdir -p ${var.remote_dir}",
      "mkdir -p ${var.remote_dir}/env",
    ]
  }

  # Copy docker-compose file
  provisioner "file" {
    source      = var.docker_compose_file
    destination = "${var.remote_dir}/docker-compose.yml"
  }

  # Copy env file
  provisioner "file" {
    source      = var.env_file
    destination = "${var.remote_dir}/env/.env"
  }

  # Copy db env file
  provisioner "file" {
    source      = var.db_env_file
    destination = "${var.remote_dir}/env/.env.db"
  }

  # Deploy with docker-compose
  provisioner "remote-exec" {
    inline = [
      "cd ${var.remote_dir}",
      "docker-compose pull",
      "docker-compose up -d"
    ]
  }
}
