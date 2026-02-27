################################################################################
# variables.tf - Input Variables for the Football Analytics Infrastructure
#
# Variables allow us to reuse this Terraform config across environments
# (dev, staging, prod) by just changing the values in terraform.tfvars.
################################################################################

variable "project_id" {
  description = "Your GCP Project ID (e.g. football-analytics-de)"
  type        = string
}

variable "region" {
  description = "GCP region for all resources. us-central1 is cheapest for most services."
  type        = string
  default     = "us-central1"
}

variable "credentials_file" {
  description = "Path to the GCP service account JSON key file"
  type        = string
  default     = "../credentials/service-account.json"
}

variable "bq_dataset_id" {
  description = "BigQuery dataset ID that will hold all football analytics tables"
  type        = string
  default     = "football_analytics"
}

variable "dataproc_cluster_name" {
  description = "Name of the Dataproc (Spark) cluster for distributed processing"
  type        = string
  default     = "football-spark-cluster"
}
