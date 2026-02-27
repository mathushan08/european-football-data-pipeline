r"""
Kaggle Data Download Script for Transfermarkt Football Dataset

This script downloads the Transfermarkt player statistics dataset from Kaggle.
Requires Kaggle API credentials to be configured.

Setup:
1. Create Kaggle account at https://www.kaggle.com/
2. Go to Account -> API -> Create New Token
3. Place kaggle.json in ~/.kaggle/ (Linux/Mac) or C:\Users\<User>\.kaggle\ (Windows)
4. Run: chmod 600 ~/.kaggle/kaggle.json (Linux/Mac only)

Usage:
    python scripts/download_data.py
"""

import os
import sys
from pathlib import Path
import json

def check_kaggle_credentials():
    """Check if Kaggle API credentials are configured."""
    kaggle_dir = Path.home() / '.kaggle'
    kaggle_json = kaggle_dir / 'kaggle.json'
    
    if not kaggle_json.exists():
        print("[ERROR] Kaggle credentials not found!")
        print("\nSetup instructions:")
        print("1. Go to https://www.kaggle.com/account")
        print("2. Click 'Create New Token' under API section")
        print(f"3. Place kaggle.json in {kaggle_dir}")
        print("4. Ensure file permissions are secure")
        return False
    
    try:
        with open(kaggle_json, 'r') as f:
            creds = json.load(f)
            if 'username' in creds and 'key' in creds:
                print(f"[OK] Kaggle credentials found for user: {creds['username']}")
                return True
    except Exception as e:
        print(f"[ERROR] Error reading Kaggle credentials: {e}")
        return False

def download_dataset():
    """Download the Transfermarkt dataset from Kaggle."""
    try:
        import kaggle
        
        # Dataset identifier
        dataset = "davidcariboo/player-scores"
        
        # Download location
        download_path = Path(__file__).parent.parent / "data" / "raw"
        download_path.mkdir(parents=True, exist_ok=True)
        
        print(f"\n[DOWNLOADING] Dataset: {dataset}")
        print(f"[DIR] Download location: {download_path}")
        
        # Download using Kaggle API
        kaggle.api.dataset_download_files(
            dataset,
            path=str(download_path),
            unzip=True,
            quiet=False
        )
        
        print("\n[OK] Dataset downloaded successfully!")
        
        # List downloaded files
        print("\n[LIST] Downloaded files:")
        for file in sorted(download_path.glob("*.csv")):
            size_mb = file.stat().st_size / (1024 * 1024)
            print(f"   - {file.name} ({size_mb:.2f} MB)")
        
        return True
        
    except ImportError:
        print("[ERROR] Kaggle package not installed!")
        print("Run: pip install kaggle")
        return False
    except Exception as e:
        print(f"[ERROR] Error downloading dataset: {e}")
        return False

def verify_data():
    """Verify that expected CSV files are present."""
    data_dir = Path(__file__).parent.parent / "data" / "raw"
    
    expected_files = [
        "competitions.csv",
        "games.csv",
        "clubs.csv",
        "players.csv",
        "appearances.csv"
    ]
    
    print("\n[VERIFY] Verifying downloaded files...")
    all_present = True
    
    for file in expected_files:
        file_path = data_dir / file
        if file_path.exists():
            print(f"   [OK] {file}")
        else:
            print(f"   [MISSING] {file} - MISSING!")
            all_present = False
    
    return all_present

def main():
    """Main execution function."""
    print("=" * 60)
    print("   Transfermarkt Football Data Download")
    print("=" * 60)
    
    # Step 1: Check credentials
    if not check_kaggle_credentials():
        sys.exit(1)
    
    # Step 2: Download dataset
    if not download_dataset():
        sys.exit(1)
    
    # Step 3: Verify files
    if not verify_data():
        print("\n[WARNING] Some expected files are missing!")
    else:
        print("\n[OK] All expected files verified!")
    
    print("\n" + "=" * 60)
    print("Next steps:")
    print("1. Check data quality: jupyter notebook")
    print("2. Set up GCP environment")
    print("3. Configure Terraform infrastructure")
    print("=" * 60)

if __name__ == "__main__":
    main()
