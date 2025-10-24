# Docker Network for local deployment
resource "docker_network" "main" {
  name = local.docker_network
  driver = "bridge"
}

# PostgreSQL Database Container
resource "docker_container" "postgres" {
  name  = "${local.app_name}-postgres"
  image = docker_image.postgres.id
  restart_policy = "always"

  ports {
    internal = local.db_port
    external = var.db_port
  }

  env = [
    "POSTGRES_USER=${var.db_user}",
    "POSTGRES_PASSWORD=${random_password.db_password.result}",
    "POSTGRES_DB=${var.db_name}"
  ]

  volumes {
    host_path      = abspath("${path.module}/../postgres_data")
    container_path = "/var/lib/postgresql/data"
    read_only      = false
  }

  networks_advanced {
    name = docker_network.main.name
  }

  healthcheck {
    test     = ["CMD-SHELL", "pg_isready -U ${var.db_user}"]
    interval = "10s"
    timeout  = "5s"
    retries  = 5
  }
}

# PostgreSQL Docker Image
resource "docker_image" "postgres" {
  name         = "postgres:${var.postgres_version}"
  keep_locally = false
  pull_image   = true
}
