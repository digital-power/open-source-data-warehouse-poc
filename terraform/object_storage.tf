# Create an Object Storage bucket for weather data
resource "scaleway_object_bucket" "weather_data" {
  name   = "weather-data-${var.environment}"
  region = var.region
}

# Create IAM application (service account)
resource "scaleway_iam_application" "weather_app" {
  name        = "weather-data-app"
  description = "Application for accessing weather data bucket"
}

# Create IAM policy for bucket access for the application
resource "scaleway_iam_policy" "weather_bucket_policy" {
  name           = "weather-bucket-access"
  description    = "Policy for weather data bucket access"
  application_id = scaleway_iam_application.weather_app.id

  rule {
    project_ids = [scaleway_object_bucket.weather_data.project_id]

    permission_set_names = [
      "ObjectStorageObjectsRead",
      "ObjectStorageObjectsWrite",
      "ObjectStorageObjectsDelete",
      "ObjectStorageBucketsRead"
    ]
  }
}

# Create API key for the application and store keys in secrets
resource "scaleway_iam_api_key" "weather_data_key" {
  application_id = scaleway_iam_application.weather_app.id
  description    = "Access key for weather data bucket access"
}

resource "scaleway_secret" "weather_data_key" {
  name        = "weather-data-access-key"
  description = "Access key for weather data bucket"
}

resource "scaleway_secret_version" "weather_data_api_access_key_version" {
  secret_id = scaleway_secret.weather_data_key.id
  data      = scaleway_iam_api_key.weather_data_key.access_key
}

resource "scaleway_secret" "weather_data_secret_key" {
  name        = "weather-data-secret-key"
  description = "Secret key for weather data bucket"
}

resource "scaleway_secret_version" "weather_data_api_secret_key_version" {
  secret_id = scaleway_secret.weather_data_secret_key.id
  data      = scaleway_iam_api_key.weather_data_key.secret_key
}

# Output the bucket name
output "weather_data_bucket_name" {
  value = scaleway_object_bucket.weather_data.name
}

# Output the IAM application ID
output "weather_data_app_id" {
  value = scaleway_iam_api_key.weather_data_key.application_id
}

# Output the API access key for the application
output "weather_data_access_key" {
  # sensitive = true
  value = scaleway_iam_api_key.weather_data_key.access_key
}

# Output the API secret key for the application
output "weather_data_api_secret_key" {
  sensitive = true
  value     = scaleway_iam_api_key.weather_data_key.secret_key
}