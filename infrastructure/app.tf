# Docker image for banking service
resource "docker_image" "app" {
  name         = "banking-service:latest"
  keep_locally = true

  build {
    context    = "${path.module}/.."
    dockerfile = "Dockerfile"
  }
}

# Docker container for FastAPI application
resource "docker_container" "app" {
  name  = "${var.app_name}-app"
  image = docker_image.app.image_id
  restart_policy = "always"

  ports {
    internal = var.container_port
    external = var.container_port
  }

  env = [
    "DATABASE_URL=postgresql://${var.db_user}:${random_password.db_password.result}@${var.app_name}-postgres:5432/banking_db",
    "SECRET_KEY=${random_password.jwt_secret.result}",
    "ALGORITHM=HS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES=30",
    "DEBUG=${var.environment != "production" ? "true" : "false"}"
  ]

  volumes {
    volume_name    = docker_volume.app_logs.name
    container_path = "/app/logs"
  }

  networks_advanced {
    name = docker_network.main.name
  }

  healthcheck {
    test     = ["CMD", "curl", "-f", "http://localhost:${var.container_port}/health"]
    interval = "10s"
    timeout  = "5s"
    retries  = 3
  }

  depends_on = [
    docker_container.postgres
  ]

  labels = {
    "project" = var.app_name
    "service" = "app"
  }
}

# Generate JWT secret
resource "random_password" "jwt_secret" {
  length  = 32
  special = true
}
