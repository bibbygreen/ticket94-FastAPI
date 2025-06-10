# Terraform for Google Cloud Compute Engine

This directory contains Terraform configurations to provision and manage Google Cloud Compute Engine instances. The configuration defaults to using the most cost-effective machine type (e2-micro) to minimize expenses.

## Resources Created

- **Compute Engine Instance**: A virtual machine instance with customizable machine type, disk size, and OS image
- **Static IP Address**: A static external IP address for the instance
- **SSH Firewall Rule**: Rule to allow SSH (port 22) traffic to the instance
- **HTTP/HTTPS Firewall Rules**: Rules to allow HTTP (port 80) and HTTPS (port 443) traffic to the instance
- **Backend Firewall Rule** (Optional): Rule to allow traffic to backend ports (8000, 8080)

## Prerequisites

- [Terraform](https://www.terraform.io/downloads.html) (v1.0 or later)
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
- A Google Cloud service account with appropriate permissions
- The service account key file (`service-key.json`) in the parent directory
- An SSH public key file (see below for generation instructions)

## Generating an SSH Key Pair

To generate an SSH key pair for use with your GCP instances:

1. **Open Terminal** on your local machine.

2. **Generate the SSH key pair** using the ssh-keygen command:
   ```bash
   ssh-keygen -t rsa -b 4096 -f ~/.ssh/gcp_vm_key -C "ubuntu"
   ```
   - `-t rsa`: Specifies the type of key to create (RSA)
   - `-b 4096`: Specifies the number of bits (4096 is more secure than the default 2048)
   - `-f ~/.ssh/gcp_vm_key`: Specifies the filename for the key pair
   - `-C "your_email@example.com"`: Adds a comment to identify the key (typically your email)

3. **When prompted for a passphrase**, you can:
   - Enter a secure passphrase (recommended for better security)
   - Press Enter twice for no passphrase (less secure but more convenient)

4. **Verify the key was created** by listing the contents of the .ssh directory:
   ```bash
   ls -la ~/.ssh | grep gcp_vm_key
   ```
   You should see:
   - `gcp_vm_key`: Your private key (keep this secure and never share it)
   - `gcp_vm_key.pub`: Your public key (this is what you'll use in Terraform)

5. **View your public key** with:

   ```bash
   cat ~/.ssh/gcp_vm_key.pub
   ```

The path to this public key file (`~/.ssh/gcp_vm_key.pub`) is what you'll use for the `ssh_pub_key_file` variable in your Terraform configuration.

## Getting Started

1. **Initialize Terraform**:

   ```bash
   terraform init
   ```

2. **Configure Variables**:

   Copy the example variables file and modify as needed:

   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

   Edit `terraform.tfvars` to set your desired values, especially:
   - `project_id`: Your GCP project ID
   - `ssh_pub_key_file`: Path to your SSH public key file (e.g., `~/.ssh/gcp_vm_key.pub` or absolute path like `/Users/username/.ssh/gcp_vm_key.pub`)
   - `boot_disk_image`: The OS image to use
   - Any other settings you want to customize

3. **Plan the Deployment**:

   ```bash
   terraform plan
   ```

   Review the plan to ensure it will create the resources you expect.

4. **Apply the Configuration**:

   ```bash
   terraform apply
   ```

   This will create all the resources defined in the configuration.

5. **Access Outputs**:

   After applying, Terraform will display output values. You can also retrieve them later:

   ```bash
   terraform output
   ```

   For example, to get the SSH connection string:

   ```bash
   terraform output ssh_connection_string
   ```

## Customization Options

### Machine Types

You can specify different machine types based on your needs:

- `e2-micro`: 2 vCPU, 1 GB memory (lowest cost)
- `e2-small`: 2 vCPU, 2 GB memory
- `e2-medium`: 2 vCPU, 4 GB memory
- `e2-standard-2`: 2 vCPU, 8 GB memory
- `e2-standard-4`: 4 vCPU, 16 GB memory
- `e2-standard-8`: 8 vCPU, 32 GB memory

For more options, see [Google Cloud machine types](https://cloud.google.com/compute/docs/machine-types).

### Boot Disk Images

Some common boot disk images:

- `debian-cloud/debian-11`
- `ubuntu-os-cloud/ubuntu-2204-lts`
- `centos-cloud/centos-7`
- `cos-cloud/cos-stable` (Container-Optimized OS)

For more options, see [Google Cloud public images](https://cloud.google.com/compute/docs/images/os-details).

### Disk Types

Available disk types:

- `pd-standard`: Standard persistent disk (HDD)
- `pd-balanced`: Balanced persistent disk (SSD)
- `pd-ssd`: SSD persistent disk
- `pd-extreme`: Extreme persistent disk (high performance)

## Updating Infrastructure

To update the infrastructure after making changes to the configuration:

1. Make your changes to the Terraform files
2. Run `terraform plan` to see what will change
3. Run `terraform apply` to apply the changes

## Destroying Infrastructure

To destroy all resources created by this configuration:

```bash
terraform destroy
```

**Warning**: This will permanently delete all resources, including any data on the instance.

## Notes

- The instance is configured to allow stopping for updates by default. This means Terraform can stop the instance to update certain properties that require the instance to be stopped.
- By default, the configuration creates a static IP address for the instance. This ensures the IP address doesn't change when the instance is stopped and started.
- SSH, HTTP, and HTTPS firewall rules are always created to ensure access to the instance.
- Backend firewall rule for ports (8000, 8080) is created by default. You can disable this by setting the `enable_backend` variable to `false` or customize the backend ports by modifying the `backend_ports` variable.
- The configuration uses a service account key file located at `../../service-key.json`. Make sure this file exists and has the necessary permissions.
