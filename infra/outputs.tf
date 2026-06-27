output "container_id" {
  description = "L'identifiant unique du conteneur déployé"
  value       = docker_container.app_container.id
}

output "container_name" {
  description = "Le nom du conteneur de l'application"
  value       = docker_container.app_container.name
}