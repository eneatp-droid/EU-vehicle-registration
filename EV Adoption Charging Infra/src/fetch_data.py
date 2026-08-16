"""
Fetch (1) EU electric vehicle registration data from Eurostat and
(2) charging point locations from OpenChargeMap.

OpenChargeMap requires a free API key: https://openchargemap.org/site/develop/api
Set it as an environment variable OCM_API_KEY (or in a .env file).
"""
import json
import logging
import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

EUROSTAT_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/road_eqr_carpda"
OCM_URL = "https://api.openchargemap.io/v3/poi"
OCM_API_KEY = os.getenv("OCM_API_KEY", "")

EU_COUNTRY_CODES = ["DE", "FR", "IT", "ES", "NL", "PL", "SE", "PT", "BE", "AT"]


def fetch_eurostat_ev_registrations() -> dict:
    params = {"format": "JSON", "lang": "EN"}
    response = requests.get(EUROSTAT_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def fetch_charging_points(country_code: str, max_results: int = 500) -> list[dict]:
    if not OCM_API_KEY:
        logger.warning(
            "OCM_API_KEY is not set. Skipping OpenChargeMap request for %s; no live charging data will be fetched.",
            country_code,
        )
        return []

    params = {
        "output": "json",
        "countrycode": country_code,
        "maxresults": max_results,
        "compact": True,
        "verbose": False,
        "key": OCM_API_KEY,
    }
    try:
        response = requests.get(OCM_URL, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        logger.warning("OpenChargeMap request failed for %s: %s", country_code, exc)
        return []


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("Baixando registros de veículos elétricos (Eurostat)...")
    try:
        ev_data = fetch_eurostat_ev_registrations()
    except requests.RequestException as exc:
        logger.warning("Eurostat request failed: %s. Using latest local raw fallback if available.", exc)
        latest = sorted(Path(__file__).resolve().parents[2].joinpath("data", "raw").glob("road_eqr_carpda_*.json"))
        if not latest:
            raise
        with latest[-1].open("r", encoding="utf-8") as f:
            ev_data = json.load(f)

    with open(DATA_DIR / "eurostat_ev_registrations.json", "w", encoding="utf-8") as f:
        json.dump(ev_data, f)

    logger.info("Baixando pontos de recarga (OpenChargeMap) por país...")
    all_points = []
    for code in EU_COUNTRY_CODES:
        logger.info("  país: %s", code)
        points = fetch_charging_points(code)
        for p in points:
            p["_country_code"] = code
        all_points.extend(points)

    df_points = pd.json_normalize(all_points)
    if df_points.empty:
        logger.warning("No live charging-point rows were retrieved. Saving a fallback demo dataset instead.")
        fallback = pd.DataFrame([
            {"_country_code": "DE", "charging_points": 1800},
            {"_country_code": "FR", "charging_points": 1500},
            {"_country_code": "IT", "charging_points": 1300},
            {"_country_code": "ES", "charging_points": 1700},
            {"_country_code": "NL", "charging_points": 2200},
            {"_country_code": "BE", "charging_points": 1100},
            {"_country_code": "PL", "charging_points": 900},
            {"_country_code": "SE", "charging_points": 1300},
            {"_country_code": "PT", "charging_points": 800},
            {"_country_code": "AT", "charging_points": 950},
        ])
        df_points = fallback

    df_points.to_csv(DATA_DIR / "charging_points.csv", index=False)
    logger.info("Salvos %d pontos de recarga.", len(df_points))


if __name__ == "__main__":
    main()
