# EU Vehicle Registration ETL Pipeline

**Streamlit:** https://eu-vehicle-registration-atp.streamlit.app/

**Theme:** Registration of new vehicles by EU country, segmented by power type (combustion, hybrid, electric).

## Why This Project

The transition to electric vehicles is one of the hottest topics in the European automotive sector right now. A pipeline that ingests, versions, and reliably provides this data is something any company in the sector (manufacturer, insurance, consulting) needs.

## Data Sources

- [Eurostat](https://ec.europa.eu/eurostat/web/main/data/database) — Public API with transportation and vehicle registration data by country
- [ECB Data Portal](https://data.ecb.europa.eu) — Series of new vehicle registrations by country (original source: ACEA)

## Suggested Architecture

```
Eurostat API ──▶ extract.py ──▶ raw/ (raw JSON/CSV)
                                   │
                                   ▼
                          transform.py (pandas)
                                   │
                                   ▼
                       PostgreSQL (staging) ──▶ dbt (dimensional modeling)
                                   │
                                   ▼
                          load.py / dbt models ──▶ mart (fact registrations)
                                   │
                                   ▼
                    Orchestrated by Airflow (dags/registration_pipeline.py)
```

## Suggested Data Model (Star)

- **fact_registrations**: country, year, month, power_type, quantity
- **dim_country**, **dim_time**, **dim_power_type**

## Steps to Evolve the Project

1. Run `src/extract.py` to download raw data (adjust Eurostat dataset code as needed).
2. Run `src/transform.py` to clean and standardize (country names, fuel types).
3. Run `src/load.py` to load into local Postgres (via Docker).
4. Create the Airflow DAG (`dags/registration_pipeline.py`) to schedule monthly execution.
5. (Advanced) Add data quality tests with `dbt tests` or `great_expectations`.

## Results / Insights (to be filled after running)

> Ex: "Electric vehicle registrations grew X% between 2023 and 2025 in the 5 largest EU markets, led by..."

## Next Steps / Expansion

- Add average price data by segment (cross with market data).
- Create dashboard with Streamlit or Metabase consuming the data mart.
- Containerize everything with Docker Compose (Postgres + Airflow + dbt).
