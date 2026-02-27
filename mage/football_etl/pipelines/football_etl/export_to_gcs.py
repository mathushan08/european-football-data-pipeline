"""
BLOCK 3: Data Exporter - Upload to Google Cloud Storage
=========================================================
PURPOSE:
  Export the transformed DataFrame to our GCS data lake bucket
  in Parquet format.

WHY PARQUET INSTEAD OF CSV?
  - Columnar storage = much faster queries in BigQuery
  - ~10x smaller file size due to compression
  - Preserves data types (dates, integers) — CSV loses them
  - Industry standard for data lakes

MAGE CONCEPT:
  An "exporter" block is the final step in a pipeline.
  It receives the transformed data and writes it to
  a destination (GCS, BigQuery, database, etc.)

OUTPUT:
  Data written to GCS at:
  gs://football-analytics-de-data-lake/processed/appearances_top5.parquet
"""

import os
import pandas as pd
from google.cloud import storage
from io import BytesIO

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


# GCS configuration (pulled from environment variables set in docker-compose)
GCS_BUCKET     = os.getenv('GCS_BUCKET', 'football-analytics-de-data-lake')
GCS_BLOB_PATH  = 'processed/appearances_top5.parquet'


@data_exporter
def export_to_gcs(data: pd.DataFrame, **kwargs) -> None:
    """Export transformed football data to GCS as Parquet."""

    print(f"[INFO] Exporting {len(data):,} rows to GCS...")
    print(f"[INFO] Destination: gs://{GCS_BUCKET}/{GCS_BLOB_PATH}")

    # ── Step 1: Convert DataFrame to Parquet bytes in memory ──────
    # We use a BytesIO buffer so we don't need to write to local disk first
    buffer = BytesIO()
    data.to_parquet(buffer, index=False, engine='pyarrow', compression='snappy')
    buffer.seek(0)  # Rewind the buffer to the beginning

    parquet_bytes = buffer.getvalue()
    size_mb = len(parquet_bytes) / (1024 * 1024)
    print(f"[INFO] Parquet size: {size_mb:.2f} MB (compressed with Snappy)")

    # ── Step 2: Upload to GCS ─────────────────────────────────────
    # The GOOGLE_APPLICATION_CREDENTIALS env var (set in docker-compose)
    # is automatically picked up by the storage client
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET)
    blob   = bucket.blob(GCS_BLOB_PATH)

    blob.upload_from_string(parquet_bytes, content_type='application/octet-stream')

    print(f"[OK] Successfully uploaded to gs://{GCS_BUCKET}/{GCS_BLOB_PATH}")
    print(f"     File size: {size_mb:.2f} MB")


@test
def test_output(*args, **kwargs) -> None:
    """Verify the file exists in GCS after export."""
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET)
    blob   = bucket.blob(GCS_BLOB_PATH)

    assert blob.exists(), f"Export failed! {GCS_BLOB_PATH} not found in GCS"
    print(f"[TEST PASSED] File confirmed in GCS: gs://{GCS_BUCKET}/{GCS_BLOB_PATH}")
