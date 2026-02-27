################################################################################
# main.tf - Core GCP Resources for Football Analytics Data Pipeline
#
# This file defines the foundational infrastructure:
#   - GCS Data Lake bucket (raw + processed data)
#   - BigQuery dataset (external + materialized tables)
#   - Dataproc cluster (distributed Spark processing)
################################################################################

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  credentials = file(var.credentials_file)
}

# ─── GCS Data Lake Bucket ────────────────────────────────────────────────────
# Stores raw CSV files from Kaggle and processed Parquet files before loading
# into BigQuery. Using STANDARD storage class for frequent access.
resource "google_storage_bucket" "data_lake" {
  name          = "${var.project_id}-data-lake"
  location      = var.region
  force_destroy = true   # Allow bucket deletion even if it has objects (dev only)

  storage_class = "STANDARD"

  # Versioning helps recover accidentally overwritten files
  versioning {
    enabled = true
  }

  # Auto-delete old raw files after 30 days to save cost
  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 30  # days
      matches_prefix = ["raw/"]
    }
  }

  uniform_bucket_level_access = true

  labels = {
    project     = "football-analytics"
    environment = "dev"
    managed_by  = "terraform"
  }
}

# Create folder structure inside the bucket
resource "google_storage_bucket_object" "raw_folder" {
  bucket  = google_storage_bucket.data_lake.name
  name    = "raw/"
  content = "placeholder"
}

resource "google_storage_bucket_object" "processed_folder" {
  bucket  = google_storage_bucket.data_lake.name
  name    = "processed/"
  content = "placeholder"
}

# ─── BigQuery Dataset ─────────────────────────────────────────────────────────
# Hosts the external table (pointing to GCS) and the dbt-materialized tables.
resource "google_bigquery_dataset" "football_analytics" {
  dataset_id    = var.bq_dataset_id
  friendly_name = "Football Analytics"
  description   = "Top-5 European league player & league performance data"
  location      = var.region

  labels = {
    project     = "football-analytics"
    environment = "dev"
    managed_by  = "terraform"
  }
}

# ─── Dataproc Cluster ─────────────────────────────────────────────────────────
# Used for distributed PySpark processing to merge appearances + competitions
# datasets into a single source of truth, then export to BigQuery.
resource "google_dataproc_cluster" "spark_cluster" {
  name   = var.dataproc_cluster_name
  region = var.region

  cluster_config {
    # Master node - coordinates the Spark job
    master_config {
      num_instances = 1
      machine_type  = "n1-standard-2"    # 2 vCPUs, 7.5 GB RAM
      disk_config {
        boot_disk_type    = "pd-standard"
        boot_disk_size_gb = 50
      }
    }

    # Worker nodes - execute Spark tasks in parallel
    worker_config {
      num_instances = 2                  # 2 workers for our dataset size
      machine_type  = "n1-standard-2"
      disk_config {
        boot_disk_type    = "pd-standard"
        boot_disk_size_gb = 50
      }
    }

    # Software configuration
    software_config {
      image_version = "2.1-debian11"    # Comes with Spark 3.3 + Python 3.10
      optional_components = ["JUPYTER"] # Useful for interactive development
    }

    # Grant the cluster access to GCS and BigQuery
    gce_cluster_config {
      service_account_scopes = [
        "https://www.googleapis.com/auth/cloud-platform"
      ]
    }
  }

  labels = {
    project     = "football-analytics"
    environment = "dev"
    managed_by  = "terraform"
  }
}
