import os
from google.cloud import bigquery

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials/service-account.json'
client = bigquery.Client(project='football-analytics-de', location='us-central1')

sql = """
SELECT 
  MIN(season_year) as from_year,
  MAX(season_year) as to_year,
  COUNT(DISTINCT season_year) as total_seasons,
  COUNT(DISTINCT player_id) as total_players,
  COUNT(*) as total_rows
FROM `football-analytics-de.football_analytics.fact_player_performance`
"""
rows = list(client.query(sql).result())
r = rows[0]
print(f"Season range : {r.from_year} to {r.to_year}  ({r.from_year}/{str(r.from_year+1)[-2:]} to {r.to_year}/{str(r.to_year+1)[-2:]})")
print(f"Total seasons: {r.total_seasons}")
print(f"Total players: {r.total_players:,}")
print(f"Total rows   : {r.total_rows:,}")
print()

sql2 = """
SELECT league_name, MIN(season_year) as from_y, MAX(season_year) as to_y, COUNT(DISTINCT season_year) as seasons
FROM `football-analytics-de.football_analytics.fact_player_performance`
GROUP BY 1 ORDER BY 1
"""
print("Per league:")
for row in client.query(sql2).result():
    print(f"  {row.league_name:<20} {row.from_y}/{str(row.from_y+1)[-2:]} - {row.to_y}/{str(row.to_y+1)[-2:]}  ({row.seasons} seasons)")
