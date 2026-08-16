"""
Fetch vehicle recall data from the NHTSA public API (no API key required).

Docs: https://www.nhtsa.gov/nhtsa-datasets-and-apis
Endpoint example:
  https://api.nhtsa.gov/recalls/recallsByVehicle?make=volkswagen&model=golf&modelYear=2022
"""
import logging
import time
from pathlib import Path

import pandas as pd
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "https://api.nhtsa.gov/recalls/recallsByVehicle"
DATA_DIR = Path(__file__).resolve().parents[1] / "data"

# Ajuste livremente essa lista de marcas/modelos/anos de interesse
TARGETS = [
    {"make": "volkswagen", "model": "golf", "modelYear": 2022},
    {"make": "bmw", "model": "3-series", "modelYear": 2022},
    {"make": "renault", "model": "clio", "modelYear": 2022},
    {"make": "stellantis", "model": "208", "modelYear": 2022},
]


def fetch_recalls_for(make: str, model: str, model_year: int) -> list[dict]:
    params = {"make": make, "model": model, "modelYear": model_year}
    response = requests.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()
    results = payload.get("results", [])
    for r in results:
        r["_query_make"] = make
        r["_query_model"] = model
        r["_query_year"] = model_year
    return results


def fetch_all(targets: list[dict]) -> pd.DataFrame:
    all_results = []
    for target in targets:
        logger.info("Fetching recalls for %s", target)
        try:
            results = fetch_recalls_for(**target)
            all_results.extend(results)
        except requests.HTTPError as exc:
            logger.warning("Falhou para %s: %s", target, exc)
        time.sleep(0.5)  # respeitar rate limit da API pública
    return pd.DataFrame(all_results)


def main():
    df = fetch_all(TARGETS)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_path = DATA_DIR / "recalls_raw.csv"
    df.to_csv(output_path, index=False)
    logger.info("Salvos %d recalls em %s", len(df), output_path)


if __name__ == "__main__":
    main()
