output "container_id" {
  description = "L'identifiant unique du conteneur déployé"
  value       = docker_container.app_container.id
}

output "container_name" {
  description = "Le nom du conteneur de l'application"
  value       = docker_container.app_container.name
}

output "staging_url" {
  description = "L'URL locale pour tester l'API FastAPI"
  value       = "http://localhost:8000"
}