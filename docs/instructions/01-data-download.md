# Phase 1: Data Download and Setup

## Prerequisites

Before starting, ensure you have:
- Python 3.9 or higher installed
- Git installed
- A Kaggle account
- Internet connection

## Step 1: Clone/Navigate to Project

```bash
cd c:\Users\Mathushan\Desktop\de_project
```

## Step 2: Set Up Python Virtual Environment

### Create virtual environment
```bash
python -m venv venv
```

### Activate the environment
**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

## Step 3: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- `pandas` - Data manipulation
- `google-cloud-storage` - GCP storage client
- `google-cloud-bigquery` - BigQuery client
- `kaggle` - Kaggle API client
- `pyspark` - Spark for local testing
- Other utilities

## Step 4: Configure Kaggle API Credentials

### Get Your Kaggle API Token

1. Go to https://www.kaggle.com/
2. Sign in or create an account
3. Click on your profile picture (top right) → **Account**
4. Scroll to **API** section
5. Click **Create New Token**
6. This downloads `kaggle.json` to your computer

### Install Kaggle Credentials

**Windows:**
```bash
# Create .kaggle directory
mkdir %USERPROFILE%\.kaggle

# Move kaggle.json there
move Downloads\kaggle.json %USERPROFILE%\.kaggle\kaggle.json
```

**Linux/Mac:**
```bash
# Create .kaggle directory
mkdir -p ~/.kaggle

# Move kaggle.json there
mv ~/Downloads/kaggle.json ~/.kaggle/kaggle.json

# Secure the file
chmod 600 ~/.kaggle/kaggle.json
```

### Verify Kaggle Setup

Test the Kaggle API:
```bash
kaggle datasets list
```

You should see a list of datasets without errors.

## Step 5: Download the Transfermarkt Dataset

Run the download script:
```bash
python scripts/download_data.py
```

Expected output:
```
============================================================
   Transfermarkt Football Data Download
============================================================
✅ Kaggle credentials found for user: your_username

📥 Downloading dataset: davidcariboo/player-scores
📁 Download location: c:\Users\Mathushan\Desktop\de_project\data\raw

Downloading player-scores.zip...
100%|████████████████████████████████████| 45.2M/45.2M [00:15<00:00, 3.01MB/s]

✅ Dataset downloaded successfully!

📋 Downloaded files:
   - appearances.csv (XXX.XX MB)
   - clubs.csv (X.XX MB)
   - competitions.csv (X.XX MB)
   - games.csv (XX.XX MB)
   - players.csv (XX.XX MB)

🔍 Verifying downloaded files...
   ✅ competitions.csv
   ✅ games.csv
   ✅ clubs.csv
   ✅ players.csv
   ✅ appearances.csv

✅ All expected files verified!
```

## Step 6: Verify Data Files

Check that all CSV files are in the `data/raw/` directory:

```bash
dir data\raw\*.csv    # Windows
ls data/raw/*.csv     # Linux/Mac
```

Expected files:
- `appearances.csv` - Player statistics per game
- `competitions.csv` - League/competition metadata
- `games.csv` - Match information
- `clubs.csv` - Team data
- `players.csv` - Player profiles

## Step 7: Explore the Data (Optional)

You can quickly explore the data using Python:

```bash
python
```

```python
import pandas as pd

# Load competitions
competitions = pd.read_csv('data/raw/competitions.csv')
print(competitions.head())
print(f"\nCompetitions: {len(competitions)} rows")

# Load appearances
appearances = pd.read_csv('data/raw/appearances.csv')
print(appearances.head())
print(f"\nAppearances: {len(appearances)} rows")

exit()
```

## Troubleshooting

### Error: "Could not find kaggle.json"
- Ensure `kaggle.json` is in the correct location:
  - Windows: `C:\Users\<YourUsername>\.kaggle\kaggle.json`
  - Linux/Mac: `~/.kaggle/kaggle.json`

### Error: "401 Unauthorized"
- Your Kaggle API token may be incorrect or expired
- Generate a new token from Kaggle → Account → API

### Error: "Module not found: kaggle"
- Activate your virtual environment
- Run: `pip install kaggle`

### Dataset download is very slow
- The dataset is large (~40-50 MB)
- Ensure stable internet connection
- Consider downloading during off-peak hours

## What's Next?

✅ Phase 1 Complete! You now have:
- Python environment set up
- Dependencies installed
- Kaggle API configured
- Raw football data downloaded

**Next Phase**: GCP Account & Environment Setup
- Create Google Cloud Platform project
- Set up service accounts and IAM
- Create and configure a VM instance
- Prepare for infrastructure deployment

See: `docs/instructions/02-gcp-setup.md`

## Learning Objectives Achieved

- ✅ Virtual environment management
- ✅ Dependency installation with pip
- ✅ API authentication and credential management
- ✅ Programmatic data download
- ✅ Data verification and exploration
- ✅ File system organization
