terraform {
  required_version = ">= 1.5.0"
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.0"
    }
  }

  # Local state file
  backend "local" {
    path = "terraform.tfstate"
  }
}

# Docker provider for local deployment
provider "docker" {
  host = var.docker_host
}

# Common configuration
locals {
  common_tags = {
    Environment = var.environment
    Project     = var.app_name
    ManagedBy   = "Terraform"
    CreatedAt   = timestamp()
  }
  
  # Local deployment ports
  app_port      = var.container_port
  db_port       = 5432
  adminer_port  = 8080
  
  # Docker network
  docker_network = "${var.app_name}-network"
}
