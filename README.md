# ⚽ End-to-End European Football Analytics Data Pipeline

![Dashboard Preview](docs/assets/dashboard_preview.png) *(Note: Add a screenshot of the Looker Studio dashboard here)*

## 📖 Project Overview
This project is an end-to-end Data Engineering pipeline that ingests, processes, and visualizes European football data (top 5 leagues: Premier League, La Liga, Bundesliga, Serie A, Ligue 1) from 2012 to 2025. It transforms raw Kaggle CSVs into a production-ready, partitioned data warehouse driving a real-time Looker Studio dashboard. 

The pipeline employs modern stack tools like **Mage AI, PySpark, dbt, BigQuery, and Terraform**, focusing on scalable architecture, data quality, and Infrastructure as Code (IaC).

---

## 🏗️ Architecture & Pipeline

```mermaid
flowchart TD
    subgraph Data Source
        K(Kaggle API) --> |Raw CSVs| L(Local Data)
    end

    subgraph Orchestration [Mage AI Orchestrator]
        L --> |Extract| M1[Mage DataLoader]
        M1 --> |Clean & Cast| M2[Mage Transformer]
        M2 --> |Load Parquet| GCS_raw[(GCS Data Lake)]
    end

    subgraph Big Data Processing [GCP Dataproc]
        GCS_raw --> |Read Parquet| Spark[PySpark Job]
        Spark --> |Complex Aggregations, \nRankings, Metrics| GCS_proc[(GCS Processed)]
        GCS_proc --> |External Table definition| BQ_Ext[BigQuery External Table]
    end

    subgraph Data Transformation [dbt (Data Build Tool)]
        BQ_Ext --> |Source| DBT_stg[dbt Staging Models\n Views]
        DBT_stg --> |Transform & Test| DBT_marts[dbt Mart Models\n Partitioned Tables]
        DBT_marts --> |fact_player_performance\ndim_leagues\ndim_players| BQ_Wh[(BigQuery Warehouse)]
    end

    subgraph Visualization [Looker Studio]
        BQ_Wh --> Dash[Interactive Dashboard\n Player & League Stats]
    end

    style K fill:#20BEFF,color:#fff
    style GCS_raw fill:#FF9900,color:#fff
    style GCS_proc fill:#FF9900,color:#fff
    style BQ_Ext fill:#4285F4,color:#fff
    style BQ_Wh fill:#4285F4,color:#fff
    style Spark fill:#E25A1C,color:#fff
    style DBT_stg fill:#FF694B,color:#fff
    style DBT_marts fill:#FF694B,color:#fff
    style Dash fill:#0459C2,color:#fff
```

## 🚀 Tech Stack & Justification

| Technology | Role | Why This Choice? |
|------------|------|------------------|
| **Google Cloud (GCP)** | Cloud Provider | Native integration between GCS, BigQuery, and Looker Studio makes it an elegant choice for Analytics. |
| **Terraform** | Infrastructure as Code | Ensures reproducibility. Automatically provisions Dataproc clusters, GCS buckets, and BigQuery datasets using version-controlled configurations. |
| **Mage AI** | Orchestration | Modern, Python-native alternative to Airflow. Provides an excellent UI, out-of-the-box data validation, and modular block-based pipeline construction. |
| **Docker** | Containerization | Simplifies local development and ensures the Mage orchestrator runs consistently across machines. |
| **Google Cloud Storage** | Data Lake | Scalable, cost-effective storage for raw CSV files and partitioned Parquet files before they are read by Spark. |
| **Apache Spark (PySpark)** | Big Data Processing | Used on a Dataproc cluster to handle heavy transformations (e.g., window functions, metric aggregations, consistency scoring) that would be too slow/expensive to run natively in a warehouse. |
| **dbt (Data Build Tool)** | Data Transformation | Brings software engineering practices (version control, testing, documentation) to SQL. Models are partitioned and clustered in BigQuery to save query costs. |
| **BigQuery** | Data Warehouse | Serverless execution, columnar storage, and unmatched querying speed for analytical workloads. |
| **Looker Studio** | Visualization | Direct hooks into BigQuery without data movement. Easily creates dynamic, dashboard-level reports with interactive date and league filters. |

---

## ⚙️ Data Modeling (dbt)

The dbt project employs a **dimensional modeling** approach with Kimball methodology:

1. **Staging (`stg_player_appearances`)**: Cleans raw data, casts data types, and standardizes names. Built as a `VIEW`.
2. **Dimension (`dim_players`, `dim_leagues`)**: Contains descriptive, all-time attributes. Built as `TABLE`.
3. **Fact (`fact_player_performance`)**: Contains granular, seasonal metrics like goals, assists, per-90 indicators, and Yellow/Red cards. 
    * ⚡ **Optimization:** Materialized as a partitioned `TABLE` (on `season_year`) and clustered on `competition_id` and `player_id` to ensure dashboard queries are highly performant and cost-efficient.

Over **27 Schema Tests** (Uniqueness, Not Null, Accepted Values) are enforced on the models to ensure data integrity before surfacing to the stakeholders.

---

## 🏃‍♂️ How to Run the Project

### 1. Requirements
- A Google Cloud Platform account
- Docker and Docker Compose installed
- Terraform installed
- Google Cloud SDK CLI (`gcloud`)

### 2. Infrastructure Setup
```bash
cd terraform
# Initialize and apply infrastructure (Buckets, BigQuery Dataset, Dataproc)
terraform init
terraform apply -var-file="terraform.tfvars"
```

### 3. Orchestration with Mage
```bash
cd mage
docker-compose up -d
```
Access `localhost:6789` and run the `football_etl` pipeline to ingest Kaggle CSVs into GCS as partitioned Parquet.

### 4. Spark Processing
```bash
# Submit the PySpark job to Dataproc to compute analytics
ps1 > .\spark\submit_spark_job.ps1
```

### 5. dbt Modeling
```bash
cd dbt
dbt deps
dbt run
dbt test
```

### 6. Dashboarding
Connect Looker Studio to the `vw_player_dashboard` mapped in BigQuery to build interactive visualisations using the custom schema.

---
*Developed as a Portfolio Project demonstrating end-to-end Data Engineering capabilities.*
