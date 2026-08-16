"""
Clean and standardize a used-car CSV (e.g. downloaded from Kaggle) into a
tidy DataFrame ready for feature engineering / modeling.

Place your downloaded CSV at ../data/raw_cars.csv before running this.
"""
import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
RAW_CSV = DATA_DIR / "raw_cars.csv"
CLEAN_CSV = DATA_DIR / "clean_cars.csv"


def load_raw() -> pd.DataFrame:
    if not RAW_CSV.exists():
        raise FileNotFoundError(
            f"{RAW_CSV} não encontrado. Baixe um dataset do Kaggle e salve nesse caminho."
        )
    return pd.read_csv(RAW_CSV)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Remove duplicatas óbvias
    df = df.drop_duplicates()

    # Exemplo de tratamento de preço (ajuste ao dataset real: remover símbolos de moeda, etc.)
    if "price" in df.columns:
        df["price"] = (
            df["price"].astype(str)
            .str.replace(r"[^\d.]", "", regex=True)
            .replace("", pd.NA)
            .astype(float)
        )
        df = df.dropna(subset=["price"])
        # Remove outliers extremos (preços absurdos)
        q_low, q_high = df["price"].quantile([0.01, 0.99])
        df = df[(df["price"] >= q_low) & (df["price"] <= q_high)]

    return df


def main():
    df_raw = load_raw()
    logger.info("Linhas antes da limpeza: %d", len(df_raw))
    df_clean = clean(df_raw)
    logger.info("Linhas depois da limpeza: %d", len(df_clean))
    df_clean.to_csv(CLEAN_CSV, index=False)
    logger.info("Dados limpos salvos em %s", CLEAN_CSV)


if __name__ == "__main__":
    main()
