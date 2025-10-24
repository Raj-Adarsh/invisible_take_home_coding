variable "environment" {
  description = "Environment name (development, staging, production)"
  type        = string
  default     = "development"
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be development, staging, or production."
  }
}

variable "app_name" {
  description = "Application name (will be used as resource prefix)"
  type        = string
  default     = "banking-service"
  validation {
    condition     = can(regex("^[a-z0-9-]{3,24}$", var.app_name))
    error_message = "App name must be 3-24 characters, lowercase letters, numbers, and hyphens only."
  }
}

variable "container_port" {
  description = "Port where the FastAPI application listens inside container"
  type        = number
  default     = 8000
  validation {
    condition     = var.container_port > 0 && var.container_port < 65536
    error_message = "Container port must be between 1 and 65535."
  }
}

variable "docker_host" {
  description = "Docker daemon socket or TCP connection string"
  type        = string
  default     = "unix:///var/run/docker.sock"
}

variable "db_port" {
  description = "Port to expose PostgreSQL database on host"
  type        = number
  default     = 5432
  validation {
    condition     = var.db_port > 0 && var.db_port < 65536
    error_message = "Database port must be between 1 and 65535."
  }
}

variable "db_user" {
  description = "Database administrator username"
  type        = string
  default     = "postgres"
  sensitive   = false
}

variable "db_password" {
    description = "Database administrator password"
    type        = string
    sensitive   = true
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "banking_db"
}

variable "postgres_version" {
  description = "PostgreSQL version to deploy"
  type        = string
  default     = "15"
}

variable "tags" {
  description = "Additional tags for resources"
  type        = map(string)
  default = {
    Project = "Banking Service"
    Type    = "Local Development"
  }
}

variable "app_port" {
    description = "Port to access the Banking Service API on host"
    type        = number
    default     = 8000
}

variable "app_name" {
    description = "Application name (will be used as resource prefix)"
    type        = string
    default     = "banking-service" 
}
