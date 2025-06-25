variable "organisation_id" {
  description = "The ID of the organization."
  type        = string
  default     = "756bf9c0-3c70-4f2b-b6b5-ef47efeb2e8a"
}

variable "region" {
  description = "The region in which the resources will be created."
  type        = string
  default     = "fr-par"
}

variable "environment" {
  description = "The environment in which the resources will be created."
  type        = string
  default     = "dev"
}