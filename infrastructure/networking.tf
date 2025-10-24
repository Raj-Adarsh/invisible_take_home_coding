# Docker Network for local deployment
resource "docker_network" "main" {
  name   = "${var.app_name}-network"
  driver = "bridge"

  ipam_config {
    subnet  = "172.20.0.0/16"
    gateway = "172.20.0.1"
  }
}

# Create directories for persistent storage
resource "null_resource" "create_docker_dirs" {
  provisioner "local-exec" {
    command = "mkdir -p ${path.module}/.docker/postgres-data ${path.module}/.docker/app-logs"
  }
}

# Docker volume for PostgreSQL data
resource "docker_volume" "postgres_data" {
  name = "${var.app_name}-postgres-data"

  depends_on = [null_resource.create_docker_dirs]
}

# Docker volume for app logs
resource "docker_volume" "app_logs" {
  name = "${var.app_name}-app-logs"

  depends_on = [null_resource.create_docker_dirs]
}
