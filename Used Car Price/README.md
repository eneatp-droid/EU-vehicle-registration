# Used Car Price Prediction Pipeline

**Theme:** Predict the price of used cars from technical characteristics using a reproducible data pipeline.

## Data sources and APIs

- **Kaggle datasets** are the main source for the model
  - Examples:
    - Cars Datasets
    - Large Dataset of Cars
- Expected file:
  - `data/raw_cars.csv`
- No API key is required unless you choose a marketplace or web-scraped source instead.

## Project structure

```
Used Car Price/
├── src/
│   ├── etl.py      # loads and cleans the Kaggle CSV
│   └── model.py    # sklearn pipeline with validation
├── data/
│   └── raw_cars.csv
├── requirements.txt
├── README.md
└── model.joblib
```

## How to run it

1. Download a used car dataset from Kaggle.
2. Save it as `data/raw_cars.csv`.
3. Run:

```bash
python src/etl.py
python src/model.py
```

## Model details

The project uses a scikit-learn pipeline with:
- imputation
- one-hot encoding for categorical variables
- standard scaling for numeric variables
- a RandomForestRegressor

## Expected metrics

Typical evaluation metrics include:
- MAE
- RMSE
- R²

## Example insight

> The final model is primarily driven by vehicle age, horsepower, and fuel type. These features usually explain most of the variation in market price.

## Immediate next steps

1. Add a clean train/test split and validation strategy for the model.
2. Compare at least three models:
   - linear regression
   - random forest regressor
   - gradient boosting regressor
3. Report and document key metrics:
   - MAE
   - RMSE
   - R²
4. Add feature importance analysis to explain price drivers.
5. Build a user-facing prediction form in the dashboard for model input values.

## Recommended roadmap

- Phase 1: standardize vehicle feature cleaning and validation.
- Phase 2: train benchmark models and compare performance.
- Phase 3: add a prediction interface and feature importance summary.
- Phase 4: package the model and expose it as a simple service or ML pipeline artifact.
