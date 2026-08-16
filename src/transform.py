"""
Transform raw Eurostat JSON-stat data into a tidy pandas DataFrame,
ready to be loaded into the staging schema.

JSON-stat format reference: https://json-stat.org/
"""
import json
import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RAW_DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
PROCESSED_DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"


def load_latest_raw_file(dataset_code: str) -> dict:
    files = sorted(RAW_DATA_DIR.glob(f"{dataset_code}_*.json"))
    if not files:
        raise FileNotFoundError(
            f"Nenhum arquivo raw encontrado para '{dataset_code}'. Rode extract.py primeiro."
        )
    latest_file = files[-1]
    logger.info("Loading raw file: %s", latest_file)
    with open(latest_file, encoding="utf-8") as f:
        return json.load(f)


def jsonstat_to_dataframe(jsonstat_data: dict) -> pd.DataFrame:
    """
    Convert a JSON-stat dict (Eurostat format) into a tidy long-format DataFrame.
    
    JSON-stat stores:
    - id: list of dimension names in order
    - size: list of dimension sizes
    - dimension: dict with dimension details (index: code->position, label: code->name)
    - value: flat array indexed by linear position
    """
    try:
        # Try pyjstat first
        from pyjstat import pyjstat
        dataset = pyjstat.Dataset.read(jsonstat_data)
        df = dataset.write("dataframe")
        return df
    except Exception:
        pass
    
    logger.info("Parsing JSON-stat manually...")
    
    dim_list = jsonstat_data.get("id", [])  # Order: ['freq', 'unit', 'mot_nrg', 'geo', 'time']
    size_list = jsonstat_data.get("size", [])  # Sizes: [1, 1, 16, 43, 13]
    dimensions = jsonstat_data.get("dimension", {})
    values = jsonstat_data.get("value", {})
    
    if not values or not dim_list or not size_list:
        logger.warning("Missing JSON-stat structure")
        return pd.DataFrame()
    
    # Build index_to_code and code_to_label mappings for each dimension
    dim_mappings = {}
    for dim_name in dim_list:
        if dim_name in dimensions:
            cat_data = dimensions[dim_name].get("category", {})
            # index: dict mapping code -> position (e.g., {'BE': 1, 'DE': 5})
            index = cat_data.get("index", {})
            # label: dict mapping code -> display name
            label = cat_data.get("label", {})
            
            # Invert index to get position -> code
            pos_to_code = {v: k for k, v in index.items()}
            dim_mappings[dim_name] = {
                "pos_to_code": pos_to_code,
                "code_to_label": label
            }
    
    # Parse flat value indices into records
    records = []
    for idx_str, value in values.items():
        if value is None:
            continue
        
        try:
            idx = int(idx_str)
            # Convert linear index to multi-dimensional indices
            multi_idx = []
            remaining = idx
            for s in reversed(size_list):
                multi_idx.insert(0, remaining % s)
                remaining //= s
            
            # Map each index to its value
            record = {}
            for dim_idx, dim_name in enumerate(dim_list):
                if dim_idx < len(multi_idx) and dim_name in dim_mappings:
                    pos = multi_idx[dim_idx]
                    pos_to_code = dim_mappings[dim_name]["pos_to_code"]
                    code_to_label = dim_mappings[dim_name]["code_to_label"]
                    
                    code = pos_to_code.get(pos, f"unknown_pos{pos}")
                    label_val = code_to_label.get(code, code)
                    record[dim_name] = label_val
            
            record["value"] = value
            records.append(record)
        except (ValueError, IndexError, KeyError) as e:
            logger.debug(f"Skipped index {idx_str}: {e}")
    
    return pd.DataFrame(records)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names, country labels and fuel-type categories."""
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Map Eurostat column names to standard names
    rename_map = {
        "geo": "country",
        "time": "year",
        "value": "registrations",
        "mot_nrg": "power_type",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    # Convert year to numeric
    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce")

    # Convert registrations to numeric
    if "registrations" in df.columns:
        df["registrations"] = pd.to_numeric(df["registrations"], errors="coerce")

    # Remove null values
    return df.dropna(subset=["registrations"]) if "registrations" in df.columns else df


def validate_processed_df(df: pd.DataFrame, dataset_code: str) -> pd.DataFrame:
    """Check that the cleaned data is usable before loading or dashboarding."""
    required_columns = {"country", "year", "power_type", "registrations"}
    missing = required_columns.difference(df.columns)
    if missing:
        raise ValueError(
            f"Dataset '{dataset_code}' is missing required columns: {sorted(missing)}"
        )
    if df.empty:
        raise ValueError(f"Dataset '{dataset_code}' produced no rows after cleaning.")
    if df["registrations"].isna().any():
        raise ValueError(f"Dataset '{dataset_code}' contains null registration values.")
    if (df["registrations"] < 0).any():
        raise ValueError(f"Dataset '{dataset_code}' contains negative registrations.")
    if df["year"].isna().any():
        raise ValueError(f"Dataset '{dataset_code}' contains null years.")

    logger.info(
        "Validation passed for '%s': %d rows across %d countries and %d years.",
        dataset_code,
        len(df),
        df["country"].nunique(),
        df["year"].nunique(),
    )
    return df


def save_processed(df: pd.DataFrame, dataset_code: str) -> Path:
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_path = PROCESSED_DATA_DIR / f"{dataset_code}_clean.csv"
    df.to_csv(output_path, index=False)
    logger.info("Processed data saved to %s (%d rows)", output_path, len(df))
    return output_path


def main(dataset_code: str = "road_eqr_carpda"):
    raw = load_latest_raw_file(dataset_code)
    df = jsonstat_to_dataframe(raw)
    df_clean = clean(df)
    validate_processed_df(df_clean, dataset_code)
    save_processed(df_clean, dataset_code)


if __name__ == "__main__":
    main()
