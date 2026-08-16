"""
Load the cleaned CSV into a PostgreSQL staging table.

Run Postgres locally first, e.g.:
    docker run --name pg-portfolio -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:16
"""
import logging
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROCESSED_DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"

DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres",
)


def get_engine():
    return create_engine(DB_URL)


def load_csv_to_staging(dataset_code: str, table_name: str = "stg_registros_veiculos"):
    csv_path = PROCESSED_DATA_DIR / f"{dataset_code}_clean.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"{csv_path} não existe. Rode transform.py primeiro.")

    df = pd.read_csv(csv_path)
    if df.empty:
        raise ValueError(f"Arquivo '{csv_path}' está vazio. Rode transform.py primeiro.")

    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS staging"))

    logger.info("Loading %d rows into table '%s'...", len(df), table_name)
    df.to_sql(table_name, engine, schema="staging", if_exists="replace", index=False)
    logger.info("Load concluído.")


def main(dataset_code: str = "road_eqr_carpda"):
    load_csv_to_staging(dataset_code)


if __name__ == "__main__":
    main()
