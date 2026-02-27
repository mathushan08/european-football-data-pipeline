"""
Create the vw_player_dashboard view in BigQuery by joining
fact_player_performance with dim_players (player names).
"""
import os
from google.cloud import bigquery

PROJECT_ID  = "football-analytics-de"
DATASET_ID  = "football_analytics"
CREDENTIALS = os.path.join(os.path.dirname(__file__), "../credentials/service-account.json")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIALS
client = bigquery.Client(project=PROJECT_ID, location="us-central1")

view_sql = f"""
CREATE OR REPLACE VIEW `{PROJECT_ID}.{DATASET_ID}.vw_player_dashboard` AS
SELECT
  f.player_id,
  COALESCE(p.player_name, CAST(f.player_id AS STRING)) AS player_name,
  f.competition_id,
  f.league_name,
  f.country_name,
  f.season_year,
  f.season_label,
  DATE(CAST(f.season_year AS STRING) || '-08-01') AS season_start_date,
  f.total_appearances,
  f.total_goals,
  f.total_assists,
  f.total_goal_contributions,
  f.total_minutes,
  f.avg_minutes_per_game,
  f.goals_per_90,
  f.assists_per_90,
  f.contributions_per_90,
  f.total_yellow_cards,
  f.total_red_cards,
  f.cards_per_90,
  f.scorer_consistency_score,
  f.goal_contribution_rate,
  f.performance_tier,
  f.goal_scorer_rank,
  f.assist_rank,
  f.is_top_10_scorer,
  f.is_top_10_assister
FROM `{PROJECT_ID}.{DATASET_ID}.fact_player_performance` f
LEFT JOIN `{PROJECT_ID}.{DATASET_ID}.dim_players` p
  ON f.player_id = p.player_id
"""

print("Creating vw_player_dashboard view...")
job = client.query(view_sql)
job.result()
print("✅ View created successfully!")

# Quick test
test_sql = f"""
SELECT player_name, league_name, season_year, total_goals, total_assists
FROM `{PROJECT_ID}.{DATASET_ID}.vw_player_dashboard`
WHERE season_year = 2023
ORDER BY total_goals DESC
LIMIT 10
"""
print("\nTop 10 scorers in 2023:")
for row in client.query(test_sql).result():
    print(f"  {row.player_name:<30} {row.league_name:<20} Goals: {row.total_goals}  Assists: {row.total_assists}")
