"""
Train a scikit-learn pipeline (preprocessing + model) to predict used car
prices, and report evaluation metrics.
"""
import logging
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
CLEAN_CSV = DATA_DIR / "clean_cars.csv"
MODEL_PATH = Path(__file__).resolve().parents[1] / "model.joblib"

TARGET = "price"
# Ajuste essas listas de acordo com as colunas reais do seu dataset
NUMERIC_FEATURES = ["engine_cc", "horsepower", "year"]
CATEGORICAL_FEATURES = ["make", "fuel_type", "transmission"]


def build_pipeline() -> Pipeline:
    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])

    preprocessor = ColumnTransformer(transformers=[
        ("num", numeric_transformer, NUMERIC_FEATURES),
        ("cat", categorical_transformer, CATEGORICAL_FEATURES),
    ])

    model = RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=-1)

    return Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", model),
    ])


def main():
    df = pd.read_csv(CLEAN_CSV)

    available_numeric = [c for c in NUMERIC_FEATURES if c in df.columns]
    available_categorical = [c for c in CATEGORICAL_FEATURES if c in df.columns]
    features = available_numeric + available_categorical

    if TARGET not in df.columns or not features:
        raise ValueError(
            "Ajuste NUMERIC_FEATURES/CATEGORICAL_FEATURES/TARGET conforme as "
            f"colunas reais do dataset: {list(df.columns)}"
        )

    X = df[features]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred) ** 0.5
    r2 = r2_score(y_test, y_pred)

    logger.info("MAE: %.2f | RMSE: %.2f | R²: %.3f", mae, rmse, r2)

    joblib.dump(pipeline, MODEL_PATH)
    logger.info("Modelo salvo em %s", MODEL_PATH)


if __name__ == "__main__":
    main()
