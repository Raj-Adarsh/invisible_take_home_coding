# Local Docker Deployment Outputs

output "app_container_id" {
  value       = docker_container.banking_app.id
  description = "ID of the Banking App container"
}

output "app_container_name" {
  value       = docker_container.banking_app.name
  description = "Name of the Banking App container"
}

output "app_url" {
  value       = "http://localhost:${var.app_port}"
  description = "URL to access the Banking Service API"
}

output "app_port" {
  value       = var.app_port
  description = "Port on which the app is running"
}

output "database_container_id" {
  value       = docker_container.postgres.id
  description = "ID of the PostgreSQL container"
}

output "database_container_name" {
  value       = docker_container.postgres.name
  description = "Name of the PostgreSQL container"
}

output "database_host" {
  value       = "localhost"
  description = "PostgreSQL server host"
}

output "database_port" {
  value       = var.db_port
  description = "PostgreSQL server port"
}

output "database_url" {
  value       = "postgresql://${var.db_user}:${var.db_password}@localhost:${var.db_port}/${var.db_name}?sslmode=disable"
  description = "PostgreSQL connection string"
  sensitive   = true
}

output "database_name" {
  value       = var.db_name
  description = "PostgreSQL database name"
}

output "docker_network_name" {
  value       = docker_network.banking_network.name
  description = "Docker network name"
}

output "docker_network_id" {
  value       = docker_network.banking_network.id
  description = "Docker network ID"
}

output "api_health_check" {
  value       = "http://localhost:${var.app_port}/health"
  description = "API health check endpoint"
}

output "api_docs_url" {
  value       = "http://localhost:${var.app_port}/docs"
  description = "Swagger API documentation URL"
}

output "openapi_schema_url" {
  value       = "http://localhost:${var.app_port}/openapi.json"
  description = "OpenAPI schema URL"
}

output "deployment_status" {
  value = {
    app_status      = docker_container.banking_app.status
    database_status = docker_container.postgres.status
    app_url         = "http://localhost:${var.app_port}"
    database_url    = "postgresql://localhost:${var.db_port}/${var.db_name}"
  }
  description = "Current deployment status"
}

output "container_logs_command" {
  value       = "docker logs ${docker_container.banking_app.name}"
  description = "Command to view app container logs"
}

output "database_logs_command" {
  value       = "docker logs ${docker_container.postgres.name}"
  description = "Command to view database container logs"
}

output "docker_compose_equivalent" {
  value = {
    description = "Equivalent docker-compose command"
    command     = "docker-compose -f docker-compose.yml up -d"
    services    = ["banking_app", "postgres"]
  }
  description = "Docker Compose equivalent for this Terraform setup"
}
