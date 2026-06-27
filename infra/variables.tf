variable "image_tag" {
  type        = string
  description = "Le tag de l'image Docker à déployer"
  default     = "latest"
}

variable "container_name" {
  type    = string
  default = "task-manager-staging"
}