# submit_spark_job.ps1
# ─────────────────────────────────────────────────────────────────────────────
# Submits the football_spark_job.py to the Dataproc cluster.
#
# WHAT THIS DOES:
#   1. Uploads the PySpark script to GCS so Dataproc can access it
#   2. Submits the job to the running Dataproc cluster
#   3. Streams logs back to this terminal
#
# HOW TO RUN:
#   cd C:\Users\Mathushan\Desktop\de_project\spark
#   .\submit_spark_job.ps1
# ─────────────────────────────────────────────────────────────────────────────

$PROJECT   = "football-analytics-de"
$BUCKET    = "football-analytics-de-data-lake"
$CLUSTER   = "football-spark-cluster"
$REGION    = "us-central1"
$SCRIPT    = "football_spark_job.py"
$GCS_SCRIPT = "gs://$BUCKET/scripts/$SCRIPT"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Football Analytics - Submitting Spark Job" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Cluster : $CLUSTER"
Write-Host "  Region  : $REGION"
Write-Host "  Script  : $GCS_SCRIPT"
Write-Host ""

# Step 1: Upload the PySpark script to GCS
Write-Host "[1/2] Uploading PySpark script to GCS..." -ForegroundColor Yellow
gcloud storage cp $SCRIPT $GCS_SCRIPT --project=$PROJECT

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to upload script to GCS" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Script uploaded: $GCS_SCRIPT" -ForegroundColor Green

# Step 2: Submit the Spark job to Dataproc
Write-Host ""
Write-Host "[2/2] Submitting Spark job to Dataproc cluster..." -ForegroundColor Yellow
Write-Host "      This will stream logs here. Takes ~3-5 minutes." -ForegroundColor Gray
Write-Host ""

gcloud dataproc jobs submit pyspark $GCS_SCRIPT `
    --cluster=$CLUSTER `
    --region=$REGION `
    --project=$PROJECT `
    -- `
    --project=$PROJECT `
    --bucket=$BUCKET `
    --bq-dataset=football_analytics `
    --bq-table=player_season_stats

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Green
    Write-Host "  [SUCCESS] Spark job completed!" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "  GCS output:" -ForegroundColor Cyan
    Write-Host "  gs://$BUCKET/spark_output/player_season_stats/" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  BigQuery table:" -ForegroundColor Cyan
    Write-Host "  $PROJECT.football_analytics.player_season_stats" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Query it in BigQuery:" -ForegroundColor Yellow
    Write-Host "  SELECT league_name, season_year, SUM(total_goals) as goals" -ForegroundColor White
    Write-Host "  FROM ``$PROJECT.football_analytics.player_season_stats``" -ForegroundColor White
    Write-Host "  GROUP BY 1, 2 ORDER BY 2 DESC, 3 DESC LIMIT 20;" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "[ERROR] Spark job failed. Check logs above." -ForegroundColor Red
    Write-Host "  Common causes:" -ForegroundColor Yellow
    Write-Host "  - Dataproc cluster not running (check GCP console)" -ForegroundColor White
    Write-Host "  - Credentials issue (check service account roles)" -ForegroundColor White
}
