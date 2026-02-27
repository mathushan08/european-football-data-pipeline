"""
BLOCK 1: Data Loader - Load Football CSVs
==========================================
PURPOSE:
  Read the two most important datasets from local data/raw/ folder:
  - appearances.csv  (player match statistics)
  - competitions.csv (competition/league info)

MAGE CONCEPT:
  A "data_loader" block is the entry point of a pipeline.
  It has no upstream blocks — its job is to fetch data
  from a source (local file, database, API, etc.)
  and pass it downstream.

OUTPUT:
  Returns a dict with two DataFrames — Mage supports
  returning multiple outputs from a single block.
"""

import os
import pandas as pd
from pathlib import Path

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader

if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@data_loader
def load_football_data(**kwargs) -> dict:
    """Load raw Transfermarkt CSV files from local storage."""

    # Resolve the data/raw path relative to this file
    # In Docker, /home/src maps to our project root
    data_dir = Path('/home/src/data/raw')

    print(f"[INFO] Loading data from: {data_dir}")

    # ── Load appearances ──────────────────────────────────────────
    # Contains: player_id, game_id, competition_id, goals, assists,
    #           yellow_cards, red_cards, minutes_played, etc.
    appearances_path = data_dir / 'appearances.csv'
    print(f"[INFO] Reading appearances.csv ({appearances_path.stat().st_size / 1e6:.1f} MB)...")
    appearances = pd.read_csv(appearances_path, low_memory=False)
    print(f"[OK]   Loaded {len(appearances):,} appearance records")

    # ── Load competitions ─────────────────────────────────────────
    # Contains: competition_id, name, country_name, type, etc.
    competitions_path = data_dir / 'competitions.csv'
    print(f"[INFO] Reading competitions.csv...")
    competitions = pd.read_csv(competitions_path, low_memory=False)
    print(f"[OK]   Loaded {len(competitions):,} competition records")

    return {
        'appearances': appearances,
        'competitions': competitions,
    }


@test
def test_output(output: dict, **kwargs) -> None:
    """Validate that the loader produced non-empty DataFrames."""
    assert output is not None, "Output is None"
    assert 'appearances' in output, "Missing appearances DataFrame"
    assert 'competitions' in output, "Missing competitions DataFrame"
    assert len(output['appearances']) > 0, "appearances is empty"
    assert len(output['competitions']) > 0, "competitions is empty"
    print("[TEST PASSED] Data loaded successfully")
