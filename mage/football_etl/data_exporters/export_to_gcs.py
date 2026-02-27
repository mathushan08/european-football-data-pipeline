import os
import pandas as pd
from google.cloud import storage
from io import BytesIO

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


GCS_BUCKET     = os.getenv('GCS_BUCKET', 'football-analytics-de-data-lake')
GCS_BLOB_PATH  = 'processed/appearances_top5.parquet'


@data_exporter
def export_to_gcs(data: pd.DataFrame, **kwargs) -> None:
    """Export transformed football data to GCS as Parquet."""
    print(f"[INFO] Exporting {len(data):,} rows to gs://{GCS_BUCKET}/{GCS_BLOB_PATH}...")

    buffer = BytesIO()
    data.to_parquet(
        buffer,
        index=False,
        engine='pyarrow',
        compression='snappy',
        coerce_timestamps='ms',
        allow_truncated_timestamps=True
    )
    buffer.seek(0)

    parquet_bytes = buffer.getvalue()
    size_mb = len(parquet_bytes) / (1024 * 1024)

    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET)
    blob   = bucket.blob(GCS_BLOB_PATH)

    blob.upload_from_string(parquet_bytes, content_type='application/octet-stream')
    print(f"[OK] Uploaded {size_mb:.2f} MB successfully.")


@test
def test_output(*args, **kwargs) -> None:
    """Verify the file exists in GCS after export."""
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET)
    blob   = bucket.blob(GCS_BLOB_PATH)
    
    assert blob.exists(), f"Export failed! {GCS_BLOB_PATH} not found in GCS"
    print(f"[TEST PASSED] File confirmed in GCS")
