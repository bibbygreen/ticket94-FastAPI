# Google Cloud project settings
project_id = "dianerp"
region     = "asia-east1"
zone       = "asia-east1-b"

# Instance settings
instance_name = "dianerp-server"
machine_type  = "e2-micro"  # 2 vCPU, 1 GB memory (cheapest option)

# Disk settings
boot_disk_size  = 20
boot_disk_type  = "pd-standard"  # Options: pd-standard, pd-balanced, pd-ssd
boot_disk_image = "ubuntu-os-cloud/ubuntu-2204-lts"  # Changed to Ubuntu 22.04 LTS

# Network settings
network_tags = ["http-server", "https-server", "ssh"]

# SSH settings
ssh_username    = "yicyun"
# Path to your SSH public key file - can use:
# - Default path with tilde: "~/.ssh/id_rsa.pub"
# - Absolute path: "/Users/username/.ssh/id_rsa.pub"
# - Relative path to a local copy: "./ssh_key.pub"
ssh_pub_key_file = "/Users/chenyicyun/.ssh/cc_id_rsa.pub"

# Instance update settings
allow_stopping_for_update = true

# IP and firewall settings
enable_backend   = true
backend_ports    = [8000, 8080]

# Labels
labels = {
  environment = "production"
  app         = "backend"
}

# Metadata
metadata = {
  enable-oslogin = "false"
}
