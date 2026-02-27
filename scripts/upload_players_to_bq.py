"""
Upload players.csv to BigQuery as dim_players table.
This gives us player names to join with fact_player_performance in Looker Studio.
"""
import pandas as pd
from google.cloud import bigquery
import os

# ── Config ──────────────────────────────────────────────────────────────────
PROJECT_ID    = "football-analytics-de"
DATASET_ID    = "football_analytics"
TABLE_ID      = "dim_players"
CREDENTIALS   = os.path.join(os.path.dirname(__file__), "../credentials/service-account.json")
PLAYERS_CSV   = os.path.join(os.path.dirname(__file__), "../data/raw/players.csv")

# ── Load CSV ────────────────────────────────────────────────────────────────
print("Reading players.csv...")
df = pd.read_csv(PLAYERS_CSV)
print(f"  Rows: {len(df):,}")
print(f"  Columns: {list(df.columns)}")

# ── Select & rename relevant columns ────────────────────────────────────────
# Build the full name: if 'name' column exists use it, else concat first+last
keep_cols = ['player_id']

# Find name columns
if 'name' in df.columns:
    df['player_name'] = df['name'].fillna('Unknown')
elif 'first_name' in df.columns and 'last_name' in df.columns:
    df['player_name'] = (
        df['first_name'].fillna('') + ' ' + df['last_name'].fillna('')
    ).str.strip()
else:
    df['player_name'] = 'Unknown'

keep_cols.append('player_name')

# Optional columns — include if they exist
for col, new_name in [
    ('position',           'position'),
    ('sub_position',       'sub_position'),
    ('nationality',        'nationality'),
    ('country_of_birth',   'country_of_birth'),
    ('date_of_birth',      'date_of_birth'),
    ('height_in_cm',       'height_cm'),
    ('market_value_in_eur','market_value_eur'),
    ('highest_market_value_in_eur', 'highest_market_value_eur'),
    ('image_url',          'image_url'),
    ('url',                'transfermarkt_url'),
]:
    if col in df.columns:
        df[new_name] = df[col]
        keep_cols.append(new_name)

dim_players = df[keep_cols].drop_duplicates(subset=['player_id'])
dim_players['player_id'] = dim_players['player_id'].astype('Int64')

print(f"\nDimension table: {len(dim_players):,} unique players")
print(dim_players[['player_id','player_name']].head(10).to_string())

# ── Upload to BigQuery ───────────────────────────────────────────────────────
print(f"\nUploading to BigQuery: {PROJECT_ID}.{DATASET_ID}.{TABLE_ID} ...")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIALS
client = bigquery.Client(project=PROJECT_ID)

table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

job_config = bigquery.LoadJobConfig(
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,   # overwrite if exists
    autodetect=True,
)

job = client.load_table_from_dataframe(dim_players, table_ref, job_config=job_config)
job.result()  # Wait for completion

table = client.get_table(table_ref)
print(f"\n✅ Uploaded successfully!")
print(f"   Table: {table_ref}")
print(f"   Rows:  {table.num_rows:,}")
print(f"   Cols:  {[f.name for f in table.schema]}")
