# Instance outputs
output "instance_name" {
  description = "The name of the compute instance"
  value       = google_compute_instance.vm_instance.name
}

output "instance_id" {
  description = "The ID of the compute instance"
  value       = google_compute_instance.vm_instance.id
}

output "instance_self_link" {
  description = "The self link of the compute instance"
  value       = google_compute_instance.vm_instance.self_link
}

output "instance_internal_ip" {
  description = "The internal IP address of the compute instance"
  value       = google_compute_instance.vm_instance.network_interface[0].network_ip
}

output "instance_external_ip" {
  description = "The external IP address of the compute instance"
  value       = google_compute_address.static_ip.address
}

output "instance_machine_type" {
  description = "The machine type of the compute instance"
  value       = google_compute_instance.vm_instance.machine_type
}

output "instance_zone" {
  description = "The zone of the compute instance"
  value       = google_compute_instance.vm_instance.zone
}

# Static IP outputs
output "static_ip_address" {
  description = "The static IP address"
  value       = google_compute_address.static_ip.address
}

output "static_ip_name" {
  description = "The name of the static IP address"
  value       = google_compute_address.static_ip.name
}

# Firewall outputs
output "ssh_firewall_name" {
  description = "The name of the SSH firewall rule"
  value       = google_compute_firewall.ssh.name
}

output "http_firewall_name" {
  description = "The name of the HTTP firewall rule"
  value       = google_compute_firewall.http.name
}

output "https_firewall_name" {
  description = "The name of the HTTPS firewall rule"
  value       = google_compute_firewall.https.name
}

output "backend_firewall_name" {
  description = "The name of the backend firewall rule (if created)"
  value       = var.enable_backend ? google_compute_firewall.backend[0].name : null
}

# SSH connection string
output "ssh_connection_string" {
  description = "The SSH connection string for the instance"
  value       = "ssh -i ~/.ssh/gcp_vm_key ${var.ssh_username}@${google_compute_address.static_ip.address}"
}
