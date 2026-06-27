terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.1"
    }
  }
}

provider "docker" {}

data "docker_network" "cicd_net" {
  name = "cicd-network"
}

resource "docker_image" "app_image" {
  name         = "task-manager-api:${var.image_tag}"
  force_remove = true
}

resource "docker_container" "app_container" {
  name  = var.container_name
  image = docker_image.app_image.image_id

  ports {
    internal = 8000
    external = 8000
  }

  networks_advanced {
    name = data.docker_network.cicd_net.name
  }

  healthcheck {
    test     = ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval = "10s"
    timeout  = "5s"
    retries  = 3
  }
}