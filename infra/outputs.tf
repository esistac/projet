output "container_id" {
  value       = docker_container.app_container.id
  description = "ID du conteneur de Staging"
}

output "container_status" {
  description = "Le statut actuel du conteneur"
  value       = docker_container.app_container.state
}