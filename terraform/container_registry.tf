resource "scaleway_registry_namespace" "weather_etl_registry" {
  name        = "weather-etl-dev"
  description = "Container registry for Weather ETL project"
}

output "registry_namespace_id" {
  value = scaleway_registry_namespace.weather_etl_registry.id
}

output "registry_endpoint" {
  value = scaleway_registry_namespace.weather_etl_registry.endpoint
}