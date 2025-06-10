# Static IP Address
resource "google_compute_address" "static_ip" {
  name  = "${var.instance_name}-ip"
  region = var.region
}

# Firewall rule for SSH
resource "google_compute_firewall" "ssh" {
  name    = "${var.project_id}-allow-ssh"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["ssh"]
}

# Firewall rule for HTTP
resource "google_compute_firewall" "http" {
  name    = "${var.project_id}-allow-http"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["80"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["http-server"]
}

# Firewall rule for HTTPS
resource "google_compute_firewall" "https" {
  name    = "${var.project_id}-allow-https"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["443"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["https-server"]
}

# Firewall rule for Backend ports
resource "google_compute_firewall" "backend" {
  count   = var.enable_backend ? 1 : 0
  name    = "${var.project_id}-allow-backend"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = var.backend_ports
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["backend-server"]
}

# Compute Engine Instance
resource "google_compute_instance" "vm_instance" {
  name         = var.instance_name
  machine_type = var.machine_type
  zone         = var.zone
  tags         = var.network_tags
  labels       = var.labels

  allow_stopping_for_update = var.allow_stopping_for_update

  boot_disk {
    initialize_params {
      image = var.boot_disk_image
      size  = var.boot_disk_size
      type  = var.boot_disk_type
    }
  }


  network_interface {
    network = "default"

    access_config {
      nat_ip = google_compute_address.static_ip.address
    }
  }

  metadata = {
    ssh-keys = "${var.ssh_username}:${file(var.ssh_pub_key_file)}"
    enable-oslogin = "false"
    block-project-ssh-keys = "true"
  }

  service_account {
    scopes = var.service_account_scopes
  }

  # Ensure the instance is created after the firewall rules
  depends_on = [
    google_compute_firewall.ssh,
    google_compute_firewall.http,
    google_compute_firewall.https,
    google_compute_firewall.backend
  ]
}
