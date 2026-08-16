# Vehicle Safety Recall Analysis

Analyze recall patterns and safety trends across vehicle makes and models.

## Data sources and APIs

- **NHTSA Recalls API** — public recall data for U.S.-market vehicles
  - Base URL: https://api.nhtsa.gov/recalls/recallsByVehicle
  - No API key required
- **Euro NCAP** — crash-test and safety ratings
  - Public web data, often needs scraping or manual data collection if you want to combine it with recall history

## Questions this project answers

1. Which brands and models have the highest recall counts in recent years?
2. Which components are most commonly associated with safety recalls?
3. Is there a relationship between sales volume and recall volume?
4. How does safety rating relate to recall history?

## Project structure

```
Vehicle safety recall analysis/
├── src/
│   └── fetch_recalls.py      # downloads recall data from NHTSA
├── notebooks/
│   └── analysis_starter.py   # exploration and charting
├── data/
│   └── recalls_raw.csv
├── requirements.txt
├── README.md
└── .gitignore
```

## How to run it

```bash
python src/fetch_recalls.py
```

This creates `data/recalls_raw.csv` with recall records for configured makes, models, and model years.

## Example outputs

- recall counts by brand
- recall counts by component type
- time trends over recent years
- model-level comparison charts

## Example insight

> Electrical and software-related issues have grown significantly in recent years, reflecting the increasing complexity of modern vehicles.

## Immediate next steps

1. Add more structured recall features:
   - make
   - model
   - model year
   - component category
   - severity or issue summary
2. Aggregate recall incidence by brand and component to identify recurring risk areas.
3. Add a normalized safety metric such as recalls per 100k vehicles sold or recalls per model year.
4. Compare recall trends to Euro NCAP ratings and model generation changes.
5. Add a dashboard summary with:
   - top recalled brands
   - top recalled components
   - recall trend over time
   - model-level comparison cards

## Recommended roadmap

- Phase 1: clean and standardize recall records.
- Phase 2: build rank and trend analysis.
- Phase 3: connect recalls to sales and safety-score datasets.
- Phase 4: package the analysis into a polished storytelling dashboard.
