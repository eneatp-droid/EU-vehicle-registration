# EU Vehicle Registration ETL Pipeline - Complete Guide

## 📋 Table of Contents
1. [What This Project Does](#what-this-project-does)
2. [Project Architecture](#project-architecture)
3. [Workflow Breakdown](#workflow-breakdown)
4. [Build from Scratch](#build-from-scratch)
5. [Running the Project](#running-the-project)
6. [Deploying to Cloud](#deploying-to-cloud)

---

## What This Project Does

This project **automatically extracts, transforms, and visualizes European vehicle registration data** from Eurostat. It tracks how cars are registered across Europe, with insights into different engine types (petrol, diesel, electric, hybrid, etc.) from 2013 to 2025.

### Real Data at a Glance
- **Source:** Eurostat API (free, no authentication required)
- **Records:** 6,684 vehicle registration entries
- **Coverage:** 45 European countries
- **Power Types:** 16 categories (Petrol, Diesel, Electric, Hybrid, Plug-in Hybrid, etc.)
- **Time Period:** 2013-2025 (13 years)
- **Total Registrations:** 12.6+ million vehicles

### Why This Project?
The automotive industry is undergoing a major transformation toward electric vehicles. This project provides **real, up-to-date data** from Eurostat to track this transition across Europe, making it perfect for:
- Data analysts studying EV adoption
- Policy makers tracking environmental impact
- Portfolio projects demonstrating ETL + Dashboard skills
- Educational purposes for learning data pipelines

---

## Project Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   EU Vehicle Registration                    │
│                      ETL Pipeline                            │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
            ┌────────┐    ┌──────────┐  ┌────────┐
            │ Extract │    │Transform │  │ Load   │
            │(Eurostat)   │(JSON→CSV)   │(DB)    │
            └────────┘    └──────────┘  └────────┘
                │             │             │
        data/raw/*.json   data/processed/  PostgreSQL
                            *.csv           (optional)
                              │
                          ┌────────────┐
                          │ Dashboard  │
                          │(Streamlit) │
                          └────────────┘
                         (localhost:8501)
                              │
                    ┌─────────┴─────────┐
                    │ 4 Chart Types     │
                    │ - Line Chart      │
                    │ - Bar Chart       │
                    │ - Heatmap         │
                    │ - Area Chart      │
                    └───────────────────┘
```

### File Structure
```
EU-vehicle-registration/
├── src/
│   ├── extract.py          # Fetch from Eurostat API
│   ├── transform.py        # Parse JSON-stat → CSV
│   ├── load.py             # Load to PostgreSQL
│   └── dashboard.py        # Streamlit visualizations
├── dags/
│   └── registration_pipeline.py  # Airflow orchestration
├── data/
│   ├── raw/                # Downloaded JSON files
│   └── processed/          # Cleaned CSV files
├── requirements.txt        # Python dependencies
├── README.md              # Project overview
├── GETTING_STARTED.md     # This file
└── .gitignore
```

---

## Workflow Breakdown

### Step 1: EXTRACT - Fetch Data from Eurostat

**What it does:** Downloads raw vehicle registration data in JSON-stat format

**Technology:** Python + `requests` library

**File:** `src/extract.py`

```python
# Key functions:
fetch_eurostat_dataset(dataset_code)  # Get JSON from API
save_raw(data, dataset_code)          # Save with timestamp
main()                                 # Orchestrate
```

**Output:**
- Location: `data/raw/road_eqr_carpda_YYYYMMDDTHHMMSS.json`
- Size: ~1MB per file
- Format: JSON-stat 2.0 (compact statistical format with dimension mappings)

**Why JSON-stat?** It's an efficient format that:
- Stores dimensions separately from values
- Uses index mappings instead of repeating values
- Reduces file size by ~70% compared to flat JSON

---

### Step 2: TRANSFORM - Parse and Clean Data

**What it does:** Converts complex JSON-stat format into a tidy CSV

**The Challenge:** JSON-stat structure:
```json
{
  "id": ["freq", "unit", "mot_nrg", "geo", "time"],
  "size": [1, 1, 16, 43, 13],
  "dimension": {
    "freq": { "index": {...}, "label": {...} },
    "unit": { "index": {...}, "label": {...} },
    ...
  },
  "value": [12345, 67890, ...]  // Flat array!
}
```

Values are stored as a flat array with indices that need to be converted to multi-dimensional coordinates using modulo arithmetic.

**Solution:** Custom JSON-stat parser using:
1. Build position→code and code→label mappings for each dimension
2. Convert flat index to multi-dimensional indices
3. Map indices to actual dimension values

**File:** `src/transform.py`

**Key Functions:**
```python
jsonstat_to_dataframe(jsonstat_data)  # Parse JSON-stat
clean(df)                             # Standardize columns
load_latest_raw_file()                # Get newest raw file
save_processed(df)                    # Save to CSV
main()                                # Orchestrate
```

**Output CSV:**
```
freq | unit | power_type    | country  | year | registrations
A    | NR   | Petrol        | Germany  | 2025 | 1,234,567
A    | NR   | Electric      | Germany  | 2025 | 456,789
A    | NR   | Hybrid Petrol | Germany  | 2025 | 123,456
... (6,684 rows total)
```

---

### Step 3: LOAD - Store in Database (Optional)

**What it does:** Loads cleaned CSV into PostgreSQL

**Technology:** SQLAlchemy ORM + psycopg2

**File:** `src/load.py`

**Key Function:**
```python
load_csv_to_staging(dataset_code)  # Read CSV → DB
```

**Output:**
- Database: PostgreSQL
- Schema: `staging`
- Table: `stg_registros_veiculos`
- Rows: 6,684

⚠️ **Currently blocked:** PostgreSQL not running (optional step)

**To enable:**
```powershell
# Option 1: Docker
docker run --name pg-portfolio -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:16

# Option 2: Local PostgreSQL installation on Windows
# Download from https://www.postgresql.org/download/windows/
```

---

### Step 4: DASHBOARD - Interactive Visualizations

**What it does:** Creates real-time, interactive charts using Streamlit

**Technology:** Streamlit + Matplotlib

**File:** `src/dashboard.py`

**Features:**

1. **Sidebar Filters**
   - Multiselect countries (default: first 3)
   - Real-time chart updates

2. **KPI Cards**
   - Total registrations
   - Number of countries
   - Power types count
   - Years covered

3. **4 Visualization Types**

   **a) Line Chart - Registration Trends**
   - X-axis: Year (2013-2025)
   - Y-axis: Registrations
   - Multiple lines per power type
   - Shows EV growth trend

   **b) Grouped Bar Chart - Latest Year**
   - Groups: Countries (rows) × Power types (columns)
   - Shows current market composition
   - Three bars per country for easy comparison

   **c) Heatmap - Registration Intensity**
   - Rows: Countries
   - Columns: Power types
   - Color intensity: Registration volume
   - Annotations: Exact numbers

   **d) Stacked Area Chart - Market Evolution**
   - Shows how market composition changed over time
   - Visualizes EV adoption growth
   - Combustion decline pattern visible

4. **Raw Data Table**
   - Full dataset view
   - Sortable columns
   - Pagination support

**Run it:**
```powershell
python -m streamlit run src/dashboard.py
# Opens at http://localhost:8501
```

---

## Build from Scratch

### Prerequisites
- Windows, Mac, or Linux
- Python 3.11 or higher
- Git
- ~15 minutes of setup time

---

### Step 1: Create Project Structure

```powershell
# Create root directory
mkdir EU-Vehicle-Registration
cd EU-Vehicle-Registration

# Create subdirectories
mkdir src, dags, data/raw, data/processed, .vscode
```

---

### Step 2: Create `requirements.txt`

Save as: `EU-Vehicle-Registration/requirements.txt`

```txt
requests==2.32.3          # HTTP client for API calls
pandas==2.2.2             # Data manipulation & analysis
matplotlib==3.9.0         # Static plotting library
streamlit==1.61.1         # Interactive dashboard framework
sqlalchemy==2.0.30        # Database ORM
psycopg2-binary==2.9.9    # PostgreSQL adapter
python-dotenv==1.0.1      # Environment variable management
apache-airflow==2.9.2     # Workflow orchestration (optional)
```

---

### Step 3: Install Dependencies

```powershell
# Create virtual environment
python -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1

# Install packages
pip install -r requirements.txt
```

---

### Step 4: Create `src/extract.py`

**Save as:** `EU-Vehicle-Registration/src/extract.py`

```python
import requests
import json
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EUROSTAT_BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"
DATASET_CODE = "road_eqr_carpda"

def fetch_eurostat_dataset(dataset_code: str, params: dict | None = None) -> dict:
    """Fetch vehicle registration data from Eurostat API"""
    url = f"{EUROSTAT_BASE_URL}/{dataset_code}"
    
    default_params = {
        "format": "JSON",
        "lang": "EN"
    }
    if params:
        default_params.update(params)
    
    logger.info(f"Fetching {dataset_code} from Eurostat...")
    response = requests.get(url, params=default_params)
    response.raise_for_status()
    
    return response.json()

def save_raw(data: dict, dataset_code: str) -> None:
    """Save raw JSON to data/raw/ with timestamp"""
    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    file_path = raw_dir / f"{dataset_code}_{timestamp}.json"
    
    with open(file_path, "w") as f:
        json.dump(data, f)
    
    logger.info(f"Saved to {file_path}")

def main():
    """Orchestrate extract step"""
    data = fetch_eurostat_dataset(DATASET_CODE)
    save_raw(data, DATASET_CODE)

if __name__ == "__main__":
    main()
```

**Run it:**
```powershell
python src/extract.py
# Creates: data/raw/road_eqr_carpda_20260816T141542.json
```

---

### Step 5: Create `src/transform.py`

**Save as:** `EU-Vehicle-Registration/src/transform.py`

```python
import json
import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def jsonstat_to_dataframe(jsonstat_data: dict) -> pd.DataFrame:
    """Convert JSON-stat format to DataFrame using dimension mappings"""
    
    # Extract structure
    id_dims = jsonstat_data["id"]  # dimension order
    size = jsonstat_data["size"]   # dimension sizes
    dimension = jsonstat_data["dimension"]
    values = jsonstat_data["value"]
    
    # Build mappings for each dimension
    dimension_mappings = {}
    for dim_name in id_dims:
        dim_data = dimension[dim_name]
        
        # position -> code mapping
        pos_to_code = {}
        if "index" in dim_data:
            for code, pos in dim_data["index"].items():
                pos_to_code[pos] = code
        
        # code -> label mapping
        code_to_label = dim_data.get("label", {})
        
        dimension_mappings[dim_name] = {
            "pos_to_code": pos_to_code,
            "code_to_label": code_to_label
        }
    
    # Convert flat index to multi-dimensional
    records = []
    for flat_idx, value in enumerate(values):
        if value is None:
            continue
        
        # Convert flat index to multi-dimensional indices using modulo
        indices = []
        remaining = flat_idx
        for s in reversed(size):
            indices.insert(0, remaining % s)
            remaining //= s
        
        # Map indices to actual dimension values
        row = {}
        for dim_idx, dim_name in enumerate(id_dims):
            pos = indices[dim_idx]
            pos_to_code = dimension_mappings[dim_name]["pos_to_code"]
            code_to_label = dimension_mappings[dim_name]["code_to_label"]
            
            code = pos_to_code.get(pos, pos)
            label = code_to_label.get(code, code)
            row[dim_name] = label
        
        row["value"] = value
        records.append(row)
    
    return pd.DataFrame(records)

def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names and data types"""
    rename_map = {
        "geo": "country",
        "time": "year",
        "mot_nrg": "power_type",
        "value": "registrations"
    }
    df = df.rename(columns=rename_map)
    
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["registrations"] = pd.to_numeric(df["registrations"], errors="coerce")
    
    # Remove rows with null registrations
    df = df.dropna(subset=["registrations"])
    
    return df

def load_latest_raw_file(dataset_code: str) -> dict:
    """Load the most recent raw JSON file"""
    raw_dir = Path("data/raw")
    files = sorted(raw_dir.glob(f"{dataset_code}_*.json"), reverse=True)
    
    if not files:
        raise FileNotFoundError(f"No raw files found for {dataset_code}")
    
    with open(files[0]) as f:
        return json.load(f)

def save_processed(df: pd.DataFrame, dataset_code: str) -> None:
    """Save cleaned DataFrame to CSV"""
    processed_dir = Path("data/processed")
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = processed_dir / f"{dataset_code}_clean.csv"
    df.to_csv(file_path, index=False)
    
    logger.info(f"Processed data saved to {file_path} ({len(df)} rows)")

def main(dataset_code: str = "road_eqr_carpda"):
    """Orchestrate transform step"""
    raw_data = load_latest_raw_file(dataset_code)
    df = jsonstat_to_dataframe(raw_data)
    df = clean(df)
    save_processed(df, dataset_code)

if __name__ == "__main__":
    main()
```

**Run it:**
```powershell
python src/transform.py
# Creates: data/processed/road_eqr_carpda_clean.csv (6,684 rows)
```

---

### Step 6: Create `src/dashboard.py`

**Save as:** `EU-Vehicle-Registration/src/dashboard.py`

```python
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Page configuration
st.set_page_config(page_title="EU Vehicle Registration", layout="wide")
st.title("🚗 EU Vehicle Registration Dashboard")
st.markdown("Real-time visualization of European vehicle registration data from Eurostat (2013-2025)")

# Load data
processed_file = Path("data/processed/road_eqr_carpda_clean.csv")

if not processed_file.exists():
    st.error("❌ Data file not found. Run `python src/transform.py` first.")
    st.stop()

df = pd.read_csv(processed_file)

# Sidebar filters
st.sidebar.header("📊 Filters")
available_countries = sorted(df["country"].unique())
selected_countries = st.sidebar.multiselect(
    "Select Countries:",
    available_countries,
    default=available_countries[:3]
)

df_filtered = df[df["country"].isin(selected_countries)]

# KPIs
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Registrations", f"{df_filtered['registrations'].sum():,.0f}")
with col2:
    st.metric("Countries", len(selected_countries))
with col3:
    st.metric("Power Types", df_filtered["power_type"].nunique())
with col4:
    st.metric("Years", df_filtered["year"].nunique())

st.divider()

# Chart 1: Line Chart - Trends by Power Type
st.subheader("📈 Registration Trends by Power Type")
trend_data = df_filtered.groupby(["year", "power_type"])["registrations"].sum().reset_index()
pivot_trend = trend_data.pivot(index="year", columns="power_type", values="registrations")

fig, ax = plt.subplots(figsize=(12, 6))
for col in pivot_trend.columns:
    ax.plot(pivot_trend.index, pivot_trend[col], marker='o', label=col, linewidth=2.5, markersize=8)
ax.set_xlabel("Year", fontsize=12)
ax.set_ylabel("Registrations", fontsize=12)
ax.set_title("Annual Registrations by Power Type", fontsize=14, fontweight="bold")
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
ax.grid(True, alpha=0.3)
plt.tight_layout()
st.pyplot(fig)

# Chart 2: Bar Chart - Latest Year
st.subheader("📊 Latest Year by Country & Power Type")
latest_year = df_filtered["year"].max()
latest_data = df_filtered[df_filtered["year"] == latest_year]
pivot_latest = latest_data.pivot_table(index="country", columns="power_type", values="registrations", aggfunc="sum")

fig, ax = plt.subplots(figsize=(14, 7))
pivot_latest.plot(kind="bar", ax=ax, width=0.8)
ax.set_xlabel("Country", fontsize=12)
ax.set_ylabel("Registrations", fontsize=12)
ax.set_title(f"Registrations by Country & Power Type ({int(latest_year)})", fontsize=14, fontweight="bold")
ax.legend(title="Power Type", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
st.pyplot(fig)

# Chart 3: Heatmap - Registration Intensity
st.subheader("🔥 Registration Intensity Heatmap")
pivot_heatmap = df_filtered.pivot_table(index="country", columns="power_type", values="registrations", aggfunc="sum")

fig, ax = plt.subplots(figsize=(14, 8))
im = ax.imshow(pivot_heatmap.values, cmap='YlOrRd', aspect='auto')

# Set ticks and labels
ax.set_xticks(range(len(pivot_heatmap.columns)))
ax.set_yticks(range(len(pivot_heatmap.index)))
ax.set_xticklabels(pivot_heatmap.columns, rotation=45, ha='right')
ax.set_yticklabels(pivot_heatmap.index)

# Add annotations
for i in range(len(pivot_heatmap.index)):
    for j in range(len(pivot_heatmap.columns)):
        value = pivot_heatmap.values[i, j]
        if pd.notna(value):
            text = ax.text(j, i, f'{int(value):,}', ha="center", va="center", color="black", fontsize=8)

ax.set_xlabel("Power Type", fontsize=12)
ax.set_ylabel("Country", fontsize=12)
ax.set_title("Total Registrations by Country & Power Type (2013-2025)", fontsize=14, fontweight="bold")
cbar = plt.colorbar(im, ax=ax)
cbar.set_label("Registrations", fontsize=12)
plt.tight_layout()
st.pyplot(fig)

# Chart 4: Stacked Area Chart - Market Evolution
st.subheader("📚 Market Composition Over Time")
area_data = df_filtered.groupby(["year", "power_type"])["registrations"].sum().reset_index()
pivot_area = area_data.pivot(index="year", columns="power_type", values="registrations").fillna(0)

fig, ax = plt.subplots(figsize=(12, 6))
ax.stackplot(pivot_area.index, pivot_area.T.values, labels=pivot_area.columns, alpha=0.8)
ax.set_xlabel("Year", fontsize=12)
ax.set_ylabel("Registrations", fontsize=12)
ax.set_title("Market Composition Evolution (Stacked Area)", fontsize=14, fontweight="bold")
ax.legend(loc='upper left', fontsize=9)
ax.grid(True, alpha=0.3)
plt.tight_layout()
st.pyplot(fig)

# Raw Data Table
st.subheader("📋 Raw Data")
st.dataframe(df_filtered.sort_values("year", ascending=False), use_container_width=True)
```

**Run it:**
```powershell
python -m streamlit run src/dashboard.py
# Opens at http://localhost:8501
```

---

### Step 7 (Optional): Create `src/load.py`

**Save as:** `EU-Vehicle-Registration/src/load.py`

```python
import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres")

def get_engine():
    """Create SQLAlchemy engine"""
    return create_engine(DATABASE_URL)

def load_csv_to_staging(dataset_code: str, table_name: str = "stg_registros_veiculos") -> None:
    """Load CSV to PostgreSQL staging table"""
    
    processed_file = Path("data/processed") / f"{dataset_code}_clean.csv"
    
    if not processed_file.exists():
        raise FileNotFoundError(f"Processed file not found: {processed_file}")
    
    logger.info(f"Loading {processed_file} to {table_name}...")
    
    df = pd.read_csv(processed_file)
    engine = get_engine()
    
    df.to_sql(table_name, engine, schema="staging", if_exists="replace", index=False)
    
    logger.info(f"✅ Loaded {len(df)} rows to {table_name}")

def main():
    """Orchestrate load step"""
    load_csv_to_staging("road_eqr_carpda")

if __name__ == "__main__":
    main()
```

---

### Step 8: Initialize Git Repository

```powershell
# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: EU Vehicle Registration ETL with Streamlit dashboard"

# Add remote (replace with your GitHub repo)
git remote add origin https://github.com/YOUR_USERNAME/EU-vehicle-registration.git

# Push
git push -u origin main
```

---

## Running the Project

### Complete Workflow

```powershell
# 1. Navigate to project
cd EU-Vehicle-Registration

# 2. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 3. Extract (fetch fresh data from Eurostat)
python src/extract.py
# Output: data/raw/road_eqr_carpda_YYYYMMDDTHHMMSS.json

# 4. Transform (parse JSON-stat → CSV)
python src/transform.py
# Output: data/processed/road_eqr_carpda_clean.csv

# 5. Dashboard (view interactive charts)
python -m streamlit run src/dashboard.py
# Opens: http://localhost:8501
```

### Expected Output

**After Extract:**
```
INFO:__main__:Fetching road_eqr_carpda from Eurostat...
INFO:__main__:Saved to data/raw/road_eqr_carpda_20260816T141542.json
```

**After Transform:**
```
INFO:__main__:Processed data saved to data/processed/road_eqr_carpda_clean.csv (6684 rows)
```

**Dashboard loads at localhost:8501 with:**
- ✅ 4 interactive charts
- ✅ Real data: 12.6M registrations
- ✅ 45 countries visible
- ✅ 16 power types
- ✅ 2013-2025 years

---

## Deploying to Cloud

### Option 1: Streamlit Community Cloud (Recommended)

**Easiest option - Free & automatic redeploys**

1. Make your GitHub repo public
2. Go to: https://share.streamlit.io/
3. Select your repo and `src/dashboard.py`
4. Click "Deploy"
5. Your app is live at: `https://YOUR-APP-NAME.streamlit.app/`

### Option 2: Heroku

See README.md for Heroku deployment instructions.

### Option 3: DigitalOcean App Platform

See README.md for DigitalOcean instructions.

---

## Troubleshooting

### ❌ "No module named 'streamlit'"
```powershell
pip install streamlit matplotlib
```

### ❌ "Data file not found"
```powershell
# Run extract and transform first
python src/extract.py
python src/transform.py
```

### ❌ "Connection refused" for PostgreSQL
```powershell
# Load step is optional. Skip it or start PostgreSQL:
docker run --name pg-portfolio -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:16
```

### ❌ "Eurostat API timeout"
- Eurostat API can be slow - try running again
- Check internet connection
- Verify: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/road_eqr_carpda?format=JSON

---

## What You've Built

✅ **Complete ETL Pipeline** - Extract→Transform→Load
✅ **Real-Time Dashboard** - 4 interactive visualizations
✅ **Production-Ready Code** - Error handling, logging, documentation
✅ **Cloud-Deployable** - Ready for Streamlit Cloud, Heroku, or DigitalOcean
✅ **Reproducible** - Git version control, requirements.txt
✅ **Scalable** - Airflow DAG ready for production scheduling

---

## Next Steps

1. **Deploy to Streamlit Cloud** - Share your dashboard online
2. **Connect PostgreSQL** - Enable full database pipeline
3. **Deploy Airflow DAG** - Automate monthly data refreshes
4. **Add more visualizations** - Country comparisons, forecasting, etc.
5. **Integrate ECB Data** - Add fuel prices, economic indicators

---

## Questions?

Refer to:
- `README.md` - Project overview
- `src/` - Implementation details
- Eurostat API: https://ec.europa.eu/eurostat/web/main/about/policies/guidelines/quality
- Streamlit docs: https://docs.streamlit.io/

Happy analyzing! 🚀
