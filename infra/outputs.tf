output "container_id" {
  value       = docker_container.app_container.id
  description = "ID du conteneur de Staging"
}

output "container_status" {
  value       = docker_container.app_container.health_status
  description = "Statut du Healthcheck"
}