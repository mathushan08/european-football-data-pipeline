"""
PySpark Job: Football Analytics - Distributed Processing on Dataproc
=====================================================================

PURPOSE:
  Read top-5 league appearances data from GCS (Parquet),
  apply Spark-native transformations, write partitioned Parquet 
  back to GCS, and create a BigQuery external table.
"""

import argparse
import sys
import subprocess
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(description='Football Analytics Spark Job')
    parser.add_argument('--project', required=True, help='GCP Project ID')
    parser.add_argument('--bucket', required=True, help='GCS bucket name')
    parser.add_argument('--input-path', default='processed/appearances_top5.parquet')
    parser.add_argument('--output-path', default='spark_output/player_season_stats')
    parser.add_argument('--bq-dataset', default='football_analytics')
    parser.add_argument('--bq-table', default='player_season_stats')
    return parser.parse_args()


# ─────────────────────────────────────────────────────────────────────────────
# Spark Session
# ─────────────────────────────────────────────────────────────────────────────

def create_spark_session(project_id: str) -> SparkSession:
    spark = (
        SparkSession.builder
        .appName("FootballAnalytics_PlayerSeasonStats")
        .config("spark.sql.parquet.int96RebaseModeInRead", "CORRECTED")
        .config("spark.sql.parquet.int96RebaseModeInWrite", "CORRECTED")
        .config("spark.sql.parquet.datetimeRebaseModeInRead", "CORRECTED")
        .config("spark.sql.parquet.datetimeRebaseModeInWrite", "CORRECTED")
        .config("spark.sql.repl.eagerEval.enabled", True)
        .getOrCreate()
    )
    spark.conf.set("parentProject", project_id)
    spark.sparkContext.setLogLevel("WARN")
    
    print(f"[OK] Spark {spark.version} session created.")
    return spark


# ─────────────────────────────────────────────────────────────────────────────
# Data Loading & Transformations
# ─────────────────────────────────────────────────────────────────────────────

def load_data(spark: SparkSession, gcs_path: str):
    print(f"[INFO] Reading Parquet from: {gcs_path}")
    df = (spark.read
        .option("mergeSchema", "false")
        .option("int96RebaseMode", "CORRECTED")
        .option("datetimeRebaseMode", "CORRECTED")
        .option("spark.sql.legacy.parquet.int96RebaseModeInRead", "CORRECTED")
        .parquet(gcs_path))
    
    return df

def transform_data(df):
    print("[INFO] Applying transformations...")
    
    # Cast column types
    df = (df
        .withColumn("goals", F.col("goals").cast(IntegerType()))
        .withColumn("assists", F.col("assists").cast(IntegerType()))
        .withColumn("minutes_played", F.col("minutes_played").cast(IntegerType()))
        .withColumn("yellow_cards", F.col("yellow_cards").cast(IntegerType()))
        .withColumn("red_cards", F.col("red_cards").cast(IntegerType()))
    )

    # Date parse and season year extraction
    df = df.withColumn("date", F.to_date(F.col("date")))
    df = df.withColumn(
        "season_year",
        F.when(F.month("date") >= 7, F.year("date")).otherwise(F.year("date") - 1)
    )

    df = df.withColumn("goal_contributions", F.col("goals") + F.col("assists"))

    # Fill nulls
    numeric_cols = {"goals": 0, "assists": 0, "minutes_played": 0, 
                    "yellow_cards": 0, "red_cards": 0, "goal_contributions": 0}
    df = df.fillna(numeric_cols)

    return df


def aggregate_player_season_stats(df):
    print("[INFO] Aggregating player season stats...")
    
    player_col = "player_id" if "player_id" in df.columns else "player_id"
    stats = (
        df
        .filter(F.col("season_year").isNotNull())
        .groupBy(player_col, "competition_id", "league_name", "country_name", "season_year")
        .agg(
            F.count("*").alias("total_appearances"),
            F.sum("goals").alias("total_goals"),
            F.sum("assists").alias("total_assists"),
            F.sum("goal_contributions").alias("total_goal_contributions"),
            F.sum("minutes_played").alias("total_minutes"),
            F.avg("minutes_played").alias("avg_minutes_per_game"),
            F.sum("yellow_cards").alias("total_yellow_cards"),
            F.sum("red_cards").alias("total_red_cards"),
            (F.sum("goals") * 90.0 / F.greatest(F.sum("minutes_played"), F.lit(1))).alias("goals_per_90"),
            (F.sum("assists") * 90.0 / F.greatest(F.sum("minutes_played"), F.lit(1))).alias("assists_per_90"),
        )
        .withColumn("goals_per_90", F.round(F.col("goals_per_90"), 3))
        .withColumn("assists_per_90", F.round(F.col("assists_per_90"), 3))
        .withColumn("avg_minutes_per_game", F.round(F.col("avg_minutes_per_game"), 1))
    )

    stats = stats.withColumn(
        "performance_tier",
        F.when(F.col("total_goals") >= 20, "Elite Scorer")
         .when(F.col("total_goals") >= 10, "Good Scorer")
         .when(F.col("total_goals") >= 5,  "Occasional Scorer")
         .otherwise("Defender/Goalkeeper/Low Scorer")
    )
    return stats


# ─────────────────────────────────────────────────────────────────────────────
# Output
# ─────────────────────────────────────────────────────────────────────────────

def write_to_gcs(df, output_gcs_path: str):
    print(f"[INFO] Writing partitioned Parquet to: {output_gcs_path}")
    (df.repartition("season_year", "competition_id")
       .write
       .mode("overwrite")
       .partitionBy("season_year", "competition_id")
       .parquet(output_gcs_path))


def create_bq_external_table(project, dataset, table, gcs_path):
    bq_table_id = f"{project}:{dataset}.{table}"
    print(f"[INFO] Creating BigQuery external table: {bq_table_id}")

    ddl = f"""
    CREATE OR REPLACE EXTERNAL TABLE `{project}.{dataset}.{table}`
    OPTIONS (
      format = 'PARQUET',
      uris   = ['{gcs_path}/*.parquet', '{gcs_path}/**/*.parquet']
    );
    """
    
    result = subprocess.run(
        ["bq", "query", "--use_legacy_sql=false", "--project_id", project, ddl],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"[OK] External table created pointing to: {gcs_path}")
    else:
        print(f"[WARN] BQ table creation failed: \n{result.stderr}")


def main():
    args = parse_args()
    input_gcs_path  = f"gs://{args.bucket}/{args.input_path}"
    output_gcs_path = f"gs://{args.bucket}/{args.output_path}"

    spark = create_spark_session(args.project)
    df_raw = load_data(spark, input_gcs_path)
    df_transformed = transform_data(df_raw)
    df_stats = aggregate_player_season_stats(df_transformed)
    
    print("[INFO] Sample output:")
    df_stats.show(5, truncate=False)
    
    write_to_gcs(df_stats, output_gcs_path)
    
    # Needs to be extracted from string building step otherwise subprocess fails
    create_bq_external_table(args.project, args.bq_dataset, args.bq_table, output_gcs_path)
    
    print("[DONE] PySpark job completed successfully.")
    spark.stop()

if __name__ == "__main__":
    main()
