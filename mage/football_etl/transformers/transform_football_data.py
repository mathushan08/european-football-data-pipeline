import pandas as pd
import numpy as np

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


# Transfermarkt competition IDs for the top-5 European leagues
TOP_5_LEAGUE_IDS = ['GB1', 'ES1', 'L1', 'IT1', 'FR1']

LEAGUE_NAMES = {
    'GB1': 'Premier League',
    'ES1': 'La Liga',
    'L1':  'Bundesliga',
    'IT1': 'Serie A',
    'FR1': 'Ligue 1',
}


@transformer
def transform_football_data(data: dict, **kwargs) -> pd.DataFrame:
    """Filter to top-5 leagues and merge appearances with competitions."""
    appearances  = data['appearances']
    competitions = data['competitions']

    print(f"[INFO] Raw appearances  : {len(appearances):,} rows")
    print(f"[INFO] Raw competitions : {len(competitions):,} rows")

    # Filter to top-5 leagues
    top5_competitions = competitions[
        competitions['competition_id'].isin(TOP_5_LEAGUE_IDS)
    ][['competition_id', 'name', 'country_name', 'type']].copy()

    print(f"[INFO] Competitions after top-5 filter: {len(top5_competitions)}")
    
    top5_appearances = appearances[
        appearances['competition_id'].isin(TOP_5_LEAGUE_IDS)
    ].copy()

    merged = top5_appearances.merge(
        top5_competitions,
        on='competition_id',
        how='left',
        suffixes=('', '_competition')
    )

    # Clean col names
    merged.columns = [col.lower().replace(' ', '_') for col in merged.columns]
    merged['league_name'] = merged['competition_id'].map(LEAGUE_NAMES)

    # Handle missing/formats
    numeric_cols = ['goals', 'assists', 'minutes_played', 'yellow_cards', 'red_cards']
    for col in numeric_cols:
        if col in merged.columns:
            merged[col] = merged[col].fillna(0).astype(int)

    if 'date' in merged.columns:
        merged['date'] = pd.to_datetime(merged['date'], errors='coerce')

    if 'goals' in merged.columns and 'assists' in merged.columns:
        merged['goal_contributions'] = merged['goals'] + merged['assists']

    print(f"[OK] Final merged dataset: {len(merged):,} rows x {len(merged.columns)} cols")
    return merged


@test
def test_output(output: pd.DataFrame, **kwargs) -> None:
    """Validate the transformed dataset."""
    assert output is not None, "Output is None"
    assert len(output) > 0, "Output DataFrame is empty"
    assert 'competition_id' in output.columns, "Missing competition_id"
    assert 'league_name' in output.columns, "Missing league_name"

    found_leagues = output['competition_id'].unique().tolist()
    for league in found_leagues:
        assert league in TOP_5_LEAGUE_IDS, f"Unexpected league: {league}"

    print(f"[TEST PASSED] {len(output):,} rows verified against top 5 leagues")
