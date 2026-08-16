# EV Adoption & Charging Infrastructure Analysis

**Theme:** Combine EV adoption by EU country with the availability of public charging infrastructure.

## Why this project matters

This is a highly relevant topic in the energy transition and decarbonisation agenda across Europe. It combines two public datasets to produce an analysis that is both strategic and visually compelling for a portfolio.

## Data sources and APIs

- **Eurostat** — public transport and vehicle registration data by country and year
  - API: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data
  - Dataset used: `road_eqr_carpda`
- **OpenChargeMap** — public EV charging station locations across Europe
  - API: https://api.openchargemap.io/v3/poi
  - API key required: set `OCM_API_KEY` in your environment or `.env` file
  - Registration: https://openchargemap.org/site/develop/api

## Questions this project answers

1. Which EU countries have the highest EV adoption rates?
2. Is there a correlation between charging-point density and EV adoption?
3. Which countries are lagging in infrastructure relative to EV growth?

## Project structure

```
EV Adoption Charging Infra/
├── src/
│   ├── fetch_data.py       # downloads Eurostat + OpenChargeMap data
│   └── merge_analyze.py    # combines data and calculates adoption metrics
├── data/
│   ├── eurostat_ev_registrations.json
│   └── charging_points.csv
├── requirements.txt
├── README.md
└── .env.example
```

## How to run it

1. Create a virtual environment.
2. Install dependencies from `requirements.txt`.
3. Set your API key:

```bash
export OCM_API_KEY="your_key_here"
```

Or on Windows PowerShell:

```powershell
$env:OCM_API_KEY="your_key_here"
```

4. Run:

```bash
python src/fetch_data.py
python src/merge_analyze.py
```

## Expected outputs

- `data/eurostat_ev_registrations.json`
- `data/charging_points.csv`
- `charging_points_map.html`

## Example insights

> Nordic markets lead both EV adoption and charging density, while some Eastern European countries show slower infrastructure growth relative to their EV fleet expansion.

## Immediate next steps

1. Add a country-level adoption metric:
   - EV registrations / total registrations
   - EV share by year
2. Add charging infrastructure metrics:
   - charging points per 100k residents
   - charging points per EV registered
3. Merge the EV and charging data into a single fact table by country and year.
4. Add a ranked comparison view:
   - best-performing countries
   - infra laggards
   - emerging EV hotspots
5. Create a dashboard insight panel summarizing:
   - adoption leaders
   - infrastructure leaders
   - countries with the biggest adoption gap

## Recommended roadmap

- Phase 1: validate and clean the EV and charging datasets.
- Phase 2: compute adoption and infrastructure ratios.
- Phase 3: add trend charts and maps to the main Streamlit dashboard.
- Phase 4: create a short business narrative for the portfolio presentation.
