"""
Extract vehicle registration data from Eurostat's public API (JSON-stat format).

Eurostat dataset used as example: road_eqr_carpda
(New registrations of passenger cars by type of motor energy).

Docs: https://ec.europa.eu/eurostat/web/main/data/web-services
"""
import json
import logging
from pathlib import Path
from datetime import datetime

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EUROSTAT_BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"
DATASET_CODE = "road_eqr_carpda"  # ajuste para o dataset que fizer sentido
RAW_DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"


def fetch_eurostat_dataset(dataset_code: str, params: dict | None = None) -> dict:
    """Fetch a dataset from the Eurostat API and return it as parsed JSON."""
    url = f"{EUROSTAT_BASE_URL}/{dataset_code}"
    default_params = {"format": "JSON", "lang": "EN"}
    if params:
        default_params.update(params)

    logger.info("Fetching dataset %s from Eurostat...", dataset_code)
    response = requests.get(url, params=default_params, timeout=30)
    response.raise_for_status()
    return response.json()


def save_raw(data: dict, dataset_code: str) -> Path:
    """Persist the raw JSON response with a timestamp, for reproducibility."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    output_path = RAW_DATA_DIR / f"{dataset_code}_{timestamp}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info("Raw data saved to %s", output_path)
    return output_path


def main():
    data = fetch_eurostat_dataset(DATASET_CODE)
    save_raw(data, DATASET_CODE)


if __name__ == "__main__":
    main()
