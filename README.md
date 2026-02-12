# Football Analytics Data Engineering Project

An end-to-end data engineering pipeline analyzing player and league performance across the top 5 European football leagues.

## 🎯 Project Overview

This project demonstrates modern data engineering practices by building a complete pipeline from data extraction to visualization:

- **Data Source**: Transfermarkt football statistics from Kaggle
- **Data Lake**: Google Cloud Storage
- **Data Warehouse**: Google BigQuery
- **Orchestration**: Mage
- **Distributed Processing**: Apache Spark on GCP Dataproc
- **Transformation**: dbt (data build tool)
- **Visualization**: Google Looker Studio

## 🏗️ Architecture

```
Kaggle API → Local Storage → Mage ETL → GCS Data Lake → 
Spark/Dataproc → BigQuery External Table → dbt → 
Materialized Views → Looker Dashboard
```

## 📊 Key Metrics Tracked

**Player Performance KPIs:**
- Goals scored
- Assists provided
- Goal contributions (goals + assists)
- Disciplinary records (yellow/red cards)

**League Performance Metrics:**
- Average goals per game by league
- Disciplinary patterns across competitions
- Top performers by league

**Leagues Covered:**
- Premier League (England)
- La Liga (Spain)
- Bundesliga (Germany)
- Serie A (Italy)
- Ligue 1 (France)

## 🛠️ Technologies Used

| Component | Technology |
|-----------|-----------|
| Cloud Platform | Google Cloud Platform (GCP) |
| Infrastructure as Code | Terraform |
| Containerization | Docker, Docker Compose |
| Orchestration | Mage |
| Distributed Computing | Apache Spark (PySpark) |
| Compute | GCP Compute Engine, Dataproc |
| Storage | GCP Cloud Storage |
| Data Warehouse | Google BigQuery |
| Transformation | dbt Cloud |
| Visualization | Google Looker Studio |
| Programming | Python, SQL |
| Version Control | Git |

## 📁 Project Structure

```
de_project/
├── data/                   # Local data storage
│   ├── raw/               # Raw CSV files from Kaggle
│   └── processed/         # Cleaned/structured data
├── mage/                  # Mage orchestration
│   ├── pipelines/         # ETL pipeline definitions
│   └── docker-compose.yml # Mage container config
├── spark/                 # PySpark jobs
│   └── jobs/             # Spark transformation scripts
├── dbt/                   # dbt project
│   └── models/           # SQL transformation models
├── terraform/             # Infrastructure as Code
│   ├── main.tf           # Resource definitions
│   ├── variables.tf      # Input variables
│   └── outputs.tf        # Output values
├── scripts/               # Utility scripts
│   └── download_data.py  # Kaggle data download
├── docs/                  # Documentation
│   └── instructions/     # Step-by-step guides
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Docker and Docker Compose
- Terraform
- GCP account with billing enabled
- Kaggle account and API credentials

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd de_project
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Kaggle API**
   - Get your API credentials from Kaggle (Account → API → Create New Token)
   - Place `kaggle.json` in `~/.kaggle/` (Linux/Mac) or `C:\Users\<User>\.kaggle\` (Windows)

4. **Set up GCP**
   - Create a GCP project
   - Enable required APIs (Compute Engine, Storage, BigQuery, Dataproc)
   - Create and download service account credentials
   - Set `GOOGLE_APPLICATION_CREDENTIALS` environment variable

5. **Download data**
   ```bash
   python scripts/download_data.py
   ```

6. **Deploy infrastructure**
   ```bash
   cd terraform
   terraform init
   terraform plan
   terraform apply
   ```

7. **Run Mage pipeline**
   ```bash
   cd mage
   docker-compose up -d
   ```

## 📖 Documentation

Detailed instructions for each phase of the project can be found in the `/docs/instructions/` directory:

1. [Data Download](docs/instructions/01-data-download.md)
2. [Environment Setup](docs/instructions/02-environment-setup.md)
3. [Terraform Infrastructure](docs/instructions/03-terraform.md)
4. [Mage Orchestration](docs/instructions/04-mage.md)
5. [Spark Processing](docs/instructions/05-spark.md)
6. [dbt Transformation](docs/instructions/06-dbt.md)
7. [Looker Dashboard](docs/instructions/07-looker.md)

## 💰 Cost Estimation

Approximate monthly GCP costs (may vary based on usage):
- Compute Engine VM: $13-50
- Cloud Storage: ~$0.02/GB
- BigQuery: First 1TB queries free
- Dataproc: ~$0.01/vCPU/hour

**Tip**: Use GCP free tier ($300 credit) and shut down resources when not in use.

## 🔒 Security Notes

- Never commit credentials (`.gitignore` configured)
- Use service accounts with minimal required permissions
- Store sensitive data in environment variables
- Rotate API keys regularly

## 📝 License

This project is for educational purposes.

## 🙏 Acknowledgments

- Dataset: [Transfermarkt on Kaggle](https://www.kaggle.com/datasets/davidcariboo/player-scores)
- Data source: Transfermarkt.com
