"""
Starter EDA for the recall dataset.

Convert this into a Jupyter notebook (jupytext) or run as-is with
`python analysis_starter.py` for a quick first look.
"""
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "recalls_raw.csv"


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["ReportReceivedDate"] = pd.to_datetime(df.get("ReportReceivedDate"), errors="coerce")
    return df


def recalls_by_make(df: pd.DataFrame):
    counts = df["_query_make"].value_counts()
    sns.barplot(x=counts.index, y=counts.values)
    plt.title("Número de recalls por marca")
    plt.ylabel("Quantidade de recalls")
    plt.xlabel("Marca")
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / "recalls_by_make.png")
    plt.close()


def recalls_over_time(df: pd.DataFrame):
    monthly = df.set_index("ReportReceivedDate").resample("ME").size()
    monthly.plot(kind="line", figsize=(10, 4))
    plt.title("Evolução mensal de recalls")
    plt.ylabel("Quantidade")
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / "recalls_over_time.png")
    plt.close()


def top_components(df: pd.DataFrame, top_n: int = 10):
    if "Component" not in df.columns:
        return None
    return df["Component"].value_counts().head(top_n)


def main():
    df = load_data()
    print(f"Total de registros: {len(df)}")
    recalls_by_make(df)
    recalls_over_time(df)
    print("Top componentes com recall:")
    print(top_components(df))


if __name__ == "__main__":
    main()
