################################################################################
# outputs.tf - Outputs displayed after `terraform apply`
#
# Outputs let you easily retrieve important resource details without
# having to navigate the GCP Console (e.g. bucket names, connection strings).
################################################################################

output "data_lake_bucket_name" {
  description = "Name of the GCS data lake bucket"
  value       = google_storage_bucket.data_lake.name
}

output "data_lake_bucket_url" {
  description = "GCS URL of the data lake bucket (use in scripts)"
  value       = "gs://${google_storage_bucket.data_lake.name}"
}

output "bigquery_dataset_id" {
  description = "BigQuery dataset ID"
  value       = google_bigquery_dataset.football_analytics.dataset_id
}

output "dataproc_cluster_name" {
  description = "Name of the Dataproc cluster"
  value       = google_dataproc_cluster.spark_cluster.name
}

output "dataproc_cluster_region" {
  description = "Region where the Dataproc cluster was created"
  value       = google_dataproc_cluster.spark_cluster.region
}
