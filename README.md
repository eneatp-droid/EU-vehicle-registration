# EU Vehicle Registration Portfolio

A portfolio of automotive and mobility analytics projects built around EV adoption, fleet intelligence, used-car value forecasting, regulatory recall analysis, and public-sector transport data.

**Live dashboard:** https://eu-vehicle-registration-atp.streamlit.app/

## Portfolio summary

This repository brings together multiple data projects under a single, coherent automotive analytics story. Each project can function independently, but together they form a stronger portfolio demonstrating end-to-end data engineering, ETL, dashboarding, and analytical storytelling.

## Projects included

| Project | Focus | Status |
| --- | --- | --- |
| EU Vehicle Registration | EU vehicle registrations by country and power type | Core project |
| EV Adoption & Charging Infra | EV growth vs charging infrastructure | Integrated |
| Fleet Telemetry Streaming | Real-time fleet sensor processing | Pipeline concept |
| Used Car Price | Vehicle price prediction from features | Model pipeline |
| Vehicle Safety Recall Analysis | Safety trends and recall analysis | Analytics project |

## Why this portfolio works

It combines:
- data ingestion from public APIs and open datasets
- transformation and validation workflows
- PostgreSQL and warehouse-style loading patterns
- dashboards and portfolio-ready visual storytelling
- a broad range of automotive use cases relevant to mobility, energy, and transport analytics

## Main project: EU Vehicle Registration

### Business value

The shift toward electrification is central to the European automotive market. A complete pipeline for vehicle registration data is useful for manufacturers, consultants, mobility companies, insurers, policy teams, and strategic analysts.

### Data sources

- [Eurostat](https://ec.europa.eu/eurostat/web/main/data/database)
  - Public API for transport and vehicle registration data by country and year
  - Base API: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data
  - Dataset example: `road_eqr_carpda`
- [ECB Data Portal](https://data.ecb.europa.eu)
  - Useful for macroeconomic and market context alongside vehicle registrations

### Architecture

```text
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
                    Airflow DAG (dags/registration_pipeline.py)
```

### Data model

- **fact_registrations**: country, year, month, power_type, quantity
- **dim_country**
- **dim_time**
- **dim_power_type**

## Full API and data source inventory

| Project | Source | API / Access | Main purpose |
| --- | --- | --- | --- |
| EU Vehicle Registration | Eurostat | https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data | Vehicle registrations by country and power type |
| EU Vehicle Registration | ECB | https://data.ecb.europa.eu | Supplementary market context |
| EV Adoption & Charging Infra | Eurostat | https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data | EV uptake by market |
| EV Adoption & Charging Infra | OpenChargeMap | https://api.openchargemap.io/v3/poi | Charging station locations |
| Fleet Telemetry Streaming | Kafka | local broker at `localhost:9092` | Real-time sensor event streaming |
| Used Car Price | Kaggle CSV | local file in `data/` | Vehicle pricing prediction |
| Vehicle Safety Recall Analysis | NHTSA | https://api.nhtsa.gov/recalls/recallsByVehicle | Recall patterns and safety issues |
| Vehicle Safety Recall Analysis | Euro NCAP | public website / manual ingestion | Safety rating comparisons |

## Key technical stack

- Python
- pandas
- Streamlit
- PostgreSQL
- dbt
- Apache Airflow
- PySpark / Kafka for streaming workflows
- scikit-learn for prediction work

## Repository structure

```text
EU-vehicle-registration/
├── README.md
├── requirements.txt
├── docker-compose.yml
├── .env.example
├── src/
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   └── dashboard.py
├── dags/
│   └── registration_pipeline.py
├── dbt/
│   └── eu_vehicle_registration/
├── EV Adoption Charging Infra/
├── Fleet telemetry streaming/
├── Used Car Price/
├── Vehicle safety recall analysis/
└── data/
```

## Local setup

### 1) Start PostgreSQL

```bash
docker compose up -d postgres
```

### 2) Create and activate a virtual environment

```bash
python -m venv .venv
. .venv/bin/activate
# Windows PowerShell:
# .\.venv\Scripts\Activate.ps1
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Run the main pipeline

```bash
python src/extract.py
python src/transform.py
python src/load.py
python -m streamlit run src/dashboard.py
```

### 5) Optional dbt workflow

```bash
cd dbt/eu_vehicle_registration
pip install dbt-postgres
DBT_PROFILES_DIR=. dbt debug
DBT_PROFILES_DIR=. dbt run
```

## Data quality and validation

The ETL layer validates that required fields are present and that no null or negative values appear in the cleaned registration dataset before output is saved.

## Example portfolio insight

> Electric-vehicle adoption is accelerating in the largest EU markets, but charging infrastructure remains uneven across regions, creating both opportunity and strategic risk for mobility stakeholders.

## Next steps and execution roadmap

### Priority 1 — stabilize the core portfolio
- Keep the single Streamlit portfolio app as the main experience.
- Ensure each tab loads from real files when available and falls back cleanly to demo data.
- Add a global filter panel for region, year, and vehicle segment across the portfolio.

### Priority 2 — strengthen project data quality
- Implement schema validation for each project before data is displayed in the dashboard.
- Add a refresh timestamp and source metadata panel in the app.
- Standardize country and model naming across all subprojects.

### Priority 3 — turn project ideas into production-ready stories
- EU Vehicle Registration: add dbt staging and mart models with trend validation.
- EV Adoption & Charging Infra: add adoption ratio and charging density metrics.
- Fleet Telemetry: add Kafka event schema, anomaly rules, and alert summaries.
- Used Car Price: add regression benchmarks, feature importance, and a prediction form.
- Vehicle Safety Recall Analysis: add component breakdown and recall-rate metrics.

### Priority 4 — portfolio polish
- Add a landing page with KPI tiles and short insight cards.
- Improve chart labeling and consistent styling across all tabs.
- Add a short “project story” summary for each tab for interviews and presentations.

### Recommended delivery sequence
1. Core ETL + dashboard stability
2. EV adoption + charging analytical layer
3. Fleet telemetry alerts and streaming pipeline
4. Used-car predictive model review
5. Recall analysis with business storyline and dashboard polish
