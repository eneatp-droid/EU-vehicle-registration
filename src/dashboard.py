"""
Unified Streamlit dashboard for the automotive portfolio projects.

Run:
    python -m streamlit run src/dashboard.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Automotive Portfolio Dashboard", layout="wide")

ROOT = Path(__file__).resolve().parents[1]
# Visual reference: The Python Graph Gallery
plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams.update({
    "axes.titlesize": 16,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "axes.grid": True,
    "axes.edgecolor": "#dfe3e8",
    "grid.alpha": 0.22,
    "legend.frameon": True,
    "legend.fancybox": True,
    "legend.facecolor": "white",
    "legend.edgecolor": "#e5e7eb",
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "font.size": 10,
    "xtick.color": "#374151",
    "ytick.color": "#374151",
})


# ----------------------------
# Helpers
# ----------------------------
@st.cache_data(show_spinner=False, ttl=30)
def load_registration_data() -> pd.DataFrame:
    csv_path = ROOT / "data" / "processed" / "road_eqr_carpda_clean.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        if not df.empty:
            return df
    df = generate_demo_registration_data()
    return df


@st.cache_data(show_spinner=False, ttl=30)
def load_charging_data() -> pd.DataFrame:
    csv_path = ROOT / "EV Adoption Charging Infra" / "data" / "charging_points.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        if not df.empty:
            return df
    return generate_charging_demo_data()


@st.cache_data(show_spinner=False, ttl=30)
def load_fleet_data() -> pd.DataFrame:
    return generate_fleet_demo_data()


@st.cache_data(show_spinner=False, ttl=30)
def load_used_car_data() -> pd.DataFrame:
    csv_path = ROOT / "Used Car Price" / "data" / "clean_cars.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        if not df.empty:
            return df
    return generate_used_car_demo_data()


@st.cache_data(show_spinner=False, ttl=30)
def load_recall_data() -> pd.DataFrame:
    csv_path = ROOT / "Vehicle safety recall analysis" / "data" / "recalls_raw.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        if not df.empty:
            return df
    return generate_recall_demo_data()


def generate_demo_registration_data() -> pd.DataFrame:
    countries = ["Germany", "France", "Italy", "Spain", "Netherlands", "Belgium", "Poland"]
    power_types = ["Combustion", "Hybrid", "Electric"]
    years = list(range(2021, 2026))
    rows = []
    for country in countries:
        for power in power_types:
            for year in years:
                base = np.random.randint(50000, 250000)
                if power == "Electric":
                    growth = 1 + (year - 2021) * 0.18
                elif power == "Hybrid":
                    growth = 1 + (year - 2021) * 0.1
                else:
                    growth = 1 - (year - 2021) * 0.04
                rows.append({
                    "country": country,
                    "power_type": power,
                    "year": year,
                    "registrations": max(int(base * growth), 1000),
                })
    return pd.DataFrame(rows)


def normalize_registration_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]
    if "power_type" not in df.columns:
        df["power_type"] = "Electric"
    if "country" not in df.columns:
        df["country"] = "Germany"
    if "year" not in df.columns:
        df["year"] = 2025
    if "registrations" not in df.columns:
        df["registrations"] = 10000
    df["year"] = pd.to_numeric(df["year"], errors="coerce").fillna(2025)
    df["registrations"] = pd.to_numeric(df["registrations"], errors="coerce").fillna(0)
    return df


def generate_charging_demo_data() -> pd.DataFrame:
    country_map = {
        "DE": ("Germany", 83.2),
        "FR": ("France", 68.0),
        "IT": ("Italy", 58.9),
        "ES": ("Spain", 48.6),
        "NL": ("Netherlands", 17.9),
        "BE": ("Belgium", 11.7),
        "PL": ("Poland", 37.7),
        "SE": ("Sweden", 10.6),
        "PT": ("Portugal", 10.3),
        "AT": ("Austria", 9.1),
    }
    rows = []
    for code, (country_name, population_millions) in country_map.items():
        for _ in range(30):
            rows.append({
                "country_code": code,
                "country_name": country_name,
                "population_millions": population_millions,
                "charging_points": int(np.random.randint(300, 3000)),
                "city": f"City-{code}",
            })
    return pd.DataFrame(rows)


def normalize_charging_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "country_code" not in df.columns:
        df["country_code"] = "DE"
    if "country_name" not in df.columns:
        df["country_name"] = df["country_code"]
    if "population_millions" not in df.columns:
        df["population_millions"] = 80.0
    if "charging_points" not in df.columns:
        df["charging_points"] = 1000
    df["population_millions"] = pd.to_numeric(df["population_millions"], errors="coerce").fillna(80.0)
    df["charging_points"] = pd.to_numeric(df["charging_points"], errors="coerce").fillna(0)
    df["charging_points_per_100k"] = (df["charging_points"] / (df["population_millions"] * 1_000_000)) * 100_000
    return df


def generate_fleet_demo_data() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    records = []
    vehicles = [f"VEH-{i:03d}" for i in range(1, 11)]
    for i in range(120):
        vehicle = vehicles[i % len(vehicles)]
        records.append({
            "timestamp": pd.Timestamp.utcnow() - pd.Timedelta(minutes=119 - i),
            "vehicle_id": vehicle,
            "speed_kmh": round(float(rng.normal(72, 18)), 1),
            "rpm": int(rng.normal(2200, 500)),
            "engine_temp_c": round(float(rng.normal(92, 12)), 1),
            "fuel_level_pct": round(float(rng.uniform(15, 100)), 1),
        })
    return pd.DataFrame(records)


def load_fleet_data() -> pd.DataFrame:
    return generate_fleet_demo_data()


def generate_used_car_demo_data() -> pd.DataFrame:
    rng = np.random.default_rng(7)
    makes = ["Volkswagen", "BMW", "Renault", "Audi", "Mercedes", "Ford"]
    fuel_types = ["Petrol", "Diesel", "Hybrid", "Electric"]
    transmissions = ["Manual", "Automatic"]
    rows = []
    for _ in range(300):
        rows.append({
            "make": rng.choice(makes),
            "fuel_type": rng.choice(fuel_types),
            "transmission": rng.choice(transmissions),
            "year": int(rng.integers(2015, 2025)),
            "horsepower": int(rng.integers(80, 350)),
            "engine_cc": int(rng.integers(1200, 4000)),
            "price": float(rng.integers(12000, 62000)),
        })
    return pd.DataFrame(rows)


def normalize_used_car_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "price" not in df.columns:
        df["price"] = 20000
    if "horsepower" not in df.columns:
        df["horsepower"] = 150
    if "year" not in df.columns:
        df["year"] = 2020
    return df


def generate_recall_demo_data() -> pd.DataFrame:
    rows = []
    for year in [2019, 2020, 2021, 2022, 2023, 2024, 2025]:
        for make, model, component in [
            ("Volkswagen", "Golf", "Airbag"),
            ("BMW", "3 Series", "Software"),
            ("Renault", "Clio", "Brakes"),
            ("Audi", "A3", "Electrical"),
            ("Ford", "Focus", "Engine"),
        ]:
            rows.append({
                "make": make,
                "model": model,
                "year": year,
                "component": component,
                "recall_count": int(np.random.randint(2, 30)),
            })
    return pd.DataFrame(rows)


def normalize_recall_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "make" not in df.columns:
        df["make"] = "Volkswagen"
    if "component" not in df.columns:
        df["component"] = "Electrical"
    if "year" not in df.columns:
        df["year"] = 2024
    return df


# ----------------------------
# Chart helpers
# ----------------------------
def chart_line(df: pd.DataFrame, x: str, y: str, title: str, hue: str | None = None):
    fig, ax = plt.subplots(figsize=(11, 4.8))
    palette = ["#2E86AB", "#F18F01", "#3A7D44", "#C73E1D", "#5A4FCF", "#9E5F4E"]
    if hue and hue in df.columns:
        for i, value in enumerate(df[hue].dropna().unique()):
            subset = df[df[hue] == value].sort_values(x)
            ax.plot(subset[x], subset[y], marker="o", linewidth=2.4, markersize=4.5, label=str(value), color=palette[i % len(palette)])
        ax.legend(frameon=True, fancybox=True, facecolor="white", edgecolor="#dfe3e8")
    else:
        series = df.sort_values(x)
        ax.plot(series[x], series[y], marker="o", linewidth=2.5, markersize=4.5, color="#2E86AB")
    ax.set_title(title)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.grid(True, alpha=0.25)
    plt.tight_layout()
    return fig


def chart_bar(df: pd.DataFrame, x: str, y: str, title: str):
    fig, ax = plt.subplots(figsize=(10, 4.6))
    df_sorted = df.sort_values(y, ascending=False)
    colors = ["#4c78a8", "#5ab4ac", "#f58518", "#e45756", "#72b7b2", "#54a24b"]
    ax.bar(df_sorted[x], df_sorted[y], color=colors[: len(df_sorted)], edgecolor="white", linewidth=0.8)
    ax.set_title(title)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.grid(axis="y", alpha=0.3)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    return fig


def chart_scatter(df: pd.DataFrame, x: str, y: str, title: str, color_col: str | None = None):
    fig, ax = plt.subplots(figsize=(10, 4.8))
    if color_col and color_col in df.columns:
        categories = df[color_col].dropna().unique()
        palette = ["#2E86AB", "#F18F01", "#3A7D44", "#C73E1D", "#5A4FCF"]
        for i, category in enumerate(categories):
            subset = df[df[color_col] == category]
            ax.scatter(subset[x], subset[y], s=35, alpha=0.7, label=str(category), color=palette[i % len(palette)])
        ax.legend(frameon=True, facecolor="white", edgecolor="#dfe3e8")
    else:
        ax.scatter(df[x], df[y], s=35, alpha=0.7, color="#2E86AB")
    ax.set_title(title)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    plt.tight_layout()
    return fig


def chart_heatmap(df: pd.DataFrame, index_name: str, columns_name: str, values_name: str, title: str):
    pivot = df.pivot_table(index=index_name, columns=columns_name, values=values_name, aggfunc="sum", fill_value=0)
    fig, ax = plt.subplots(figsize=(10, 5))
    img = ax.imshow(pivot.values, cmap="YlOrRd", aspect="auto")
    ax.set_title(title)
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            ax.text(j, i, f"{int(pivot.iloc[i, j])}", ha="center", va="center", color="black", fontsize=8)
    fig.colorbar(img, ax=ax, shrink=0.85)
    plt.tight_layout()
    return fig


def chart_boxplot(df: pd.DataFrame, x: str, y: str, title: str):
    fig, ax = plt.subplots(figsize=(10, 4.8))
    groups = [df[df[x] == value][y].dropna() for value in df[x].dropna().unique()]
    ax.boxplot(groups, labels=[str(v) for v in df[x].dropna().unique()], patch_artist=True)
    for patch, color in zip(ax.artists, ["#2E86AB", "#F18F01", "#3A7D44", "#C73E1D", "#5A4FCF"]):
        patch.set_facecolor(color)
    ax.set_title(title)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    return fig


# ----------------------------
# Streamlit app
# ----------------------------
st.title("🚗 Automotive Portfolio Dashboard")
st.caption("Visual language inspired by The Python Graph Gallery — integrated view across EV registration, charging, fleet telemetry, used-car pricing, and vehicle safety recall analysis")

with st.sidebar:
    st.header("Portfolio controls")
    data_mode = st.radio("Data mode", ["Live + demo fallback", "Demo only"], index=0)
    refresh_button = st.button("Refresh live data")
    if refresh_button:
        st.cache_data.clear()
        st.rerun()

project_tabs = st.tabs([
    "EV Registration",
    "EV Adoption + Charging",
    "Fleet Telemetry",
    "Used Car Price",
    "Vehicle Safety Recalls",
])

with project_tabs[0]:
    df = load_registration_data()
    df = normalize_registration_data(df)
    if data_mode == "Demo only":
        df = generate_demo_registration_data()
    selected_countries = st.multiselect("Countries", sorted(df["country"].dropna().unique()), default=sorted(df["country"].dropna().unique())[:3])
    selected_power = st.multiselect("Power types", sorted(df["power_type"].dropna().unique()), default=sorted(df["power_type"].dropna().unique()))
    year_min, year_max = int(df["year"].min()), int(df["year"].max())
    year_range = st.slider("Year range", year_min, year_max, (year_min, year_max))
    df = df[df["country"].isin(selected_countries)]
    df = df[df["power_type"].isin(selected_power)]
    df = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])]

    st.subheader("EV registration pipeline")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total registrations", f"{df['registrations'].sum():,.0f}")
    with col2:
        st.metric("Countries tracked", df['country'].nunique())
    with col3:
        st.metric("Power types", df['power_type'].nunique())
    with col4:
        st.metric("Years covered", f"{int(df['year'].min())}-{int(df['year'].max())}")

    trend = df.groupby(["year", "power_type"], as_index=False)["registrations"].sum()
    st.pyplot(chart_line(trend, "year", "registrations", "Registration trend by power type", "power_type"))

    latest = df[df["year"] == df["year"].max()].groupby("country", as_index=False)["registrations"].sum()
    st.pyplot(chart_bar(latest, "country", "registrations", "Latest-year registrations by country"))

    heatmap_df = df.groupby(["country", "power_type"], as_index=False)["registrations"].sum()
    st.pyplot(chart_heatmap(heatmap_df, "country", "power_type", "registrations", "Heatmap: registrations by country and power type"))
    st.dataframe(df.head(20), width="stretch")

with project_tabs[1]:
    df = load_charging_data()
    df = normalize_charging_data(df)
    if data_mode == "Demo only":
        df = generate_charging_demo_data()
        df = normalize_charging_data(df)
    selected_countries = st.multiselect("Countries", sorted(df["country_name"].dropna().unique()), default=sorted(df["country_name"].dropna().unique()))
    df = df[df["country_name"].isin(selected_countries)]

    st.subheader("EV adoption + charging infrastructure")
    total = df["charging_points"].sum()
    avg_density = df["charging_points_per_100k"].mean() if "charging_points_per_100k" in df.columns else 0
    countries = df["country_name"].nunique() if "country_name" in df.columns else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total charging points", f"{total:,.0f}")
    with col2:
        st.metric("Avg charging points per 100k", f"{avg_density:,.1f}")
    with col3:
        st.metric("Countries", countries)

    by_country = df.groupby("country_name", as_index=False).agg(
        charging_points=("charging_points", "sum"),
        charging_points_per_100k=("charging_points_per_100k", "mean"),
    )
    st.pyplot(chart_bar(by_country, "country_name", "charging_points_per_100k", "Charging points per 100k inhabitants by country"))
    st.pyplot(chart_bar(by_country, "country_name", "charging_points", "Charging points by country"))
    st.info("This section compares charging infrastructure density to population size, which is more meaningful than raw counts alone.")

with project_tabs[2]:
    df = load_fleet_data()
    if data_mode == "Demo only":
        df = generate_fleet_demo_data()
    selected_vehicles = st.multiselect("Vehicles", sorted(df["vehicle_id"].dropna().unique()), default=sorted(df["vehicle_id"].dropna().unique())[:5])
    df = df[df["vehicle_id"].isin(selected_vehicles)]

    st.subheader("Fleet telemetry streaming")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Vehicles", df["vehicle_id"].nunique())
    with col2:
        st.metric("Avg speed", f"{df['speed_kmh'].mean():.1f} km/h")
    with col3:
        st.metric("Max engine temp", f"{df['engine_temp_c'].max():.1f}°C")

    agg = df.groupby("vehicle_id", as_index=False).agg(avg_speed=("speed_kmh", "mean"), avg_rpm=("rpm", "mean"))
    st.pyplot(chart_bar(agg, "vehicle_id", "avg_speed", "Average speed by vehicle"))

    by_time = df.groupby(df["timestamp"].dt.floor("10min")).agg(avg_rpm=("rpm", "mean"), avg_speed=("speed_kmh", "mean"))
    st.pyplot(chart_line(by_time.reset_index(), "timestamp", "avg_rpm", "Average RPM over time"))
    st.dataframe(df.head(20), width="stretch")

with project_tabs[3]:
    df = load_used_car_data()
    df = normalize_used_car_data(df)
    if data_mode == "Demo only":
        df = generate_used_car_demo_data()
    selected_makes = st.multiselect("Makes", sorted(df["make"].dropna().unique()), default=sorted(df["make"].dropna().unique())[:3])
    selected_fuels = st.multiselect("Fuel types", sorted(df["fuel_type"].dropna().unique()), default=sorted(df["fuel_type"].dropna().unique()))
    year_min, year_max = int(df["year"].min()), int(df["year"].max())
    year_range = st.slider("Year range", year_min, year_max, (year_min, year_max), key="used_car_year_range")
    df = df[df["make"].isin(selected_makes)]
    df = df[df["fuel_type"].isin(selected_fuels)]
    df = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])]

    st.subheader("Used car price prediction")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rows", len(df))
    with col2:
        st.metric("Average price", f"€{df['price'].mean():,.0f}")
    with col3:
        st.metric("Makes", df["make"].nunique())

    by_fuel = df.groupby("fuel_type", as_index=False)["price"].mean().sort_values("price", ascending=False)
    st.pyplot(chart_bar(by_fuel, "fuel_type", "price", "Average price by fuel type"))
    st.pyplot(chart_boxplot(df[["fuel_type", "price"]].copy(), "fuel_type", "price", "Price distribution by fuel type"))

    by_make = df.groupby("make", as_index=False)["price"].mean().sort_values("price", ascending=False)
    st.pyplot(chart_bar(by_make, "make", "price", "Average price by make"))
    scatter = df[["horsepower", "price", "fuel_type"]].copy()
    st.pyplot(chart_scatter(scatter, "horsepower", "price", "Price vs horsepower by fuel type", "fuel_type"))
    st.dataframe(df.head(20), width="stretch")

with project_tabs[4]:
    df = load_recall_data()
    df = normalize_recall_data(df)
    if data_mode == "Demo only":
        df = generate_recall_demo_data()
    selected_makes = st.multiselect("Makes", sorted(df["make"].dropna().unique()), default=sorted(df["make"].dropna().unique()))
    selected_components = st.multiselect("Components", sorted(df["component"].dropna().unique()), default=sorted(df["component"].dropna().unique()))
    year_min, year_max = int(df["year"].min()), int(df["year"].max())
    year_range = st.slider("Year range", year_min, year_max, (year_min, year_max), key="recall_year_range")
    df = df[df["make"].isin(selected_makes)]
    df = df[df["component"].isin(selected_components)]
    df = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])]

    st.subheader("Vehicle safety recall analysis")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Recall records", len(df))
    with col2:
        st.metric("Brands", df["make"].nunique())
    with col3:
        st.metric("Top component", df["component"].mode().iloc[0] if not df.empty else "N/A")

    by_make = df.groupby("make", as_index=False)["recall_count"].sum().sort_values("recall_count", ascending=False)
    st.pyplot(chart_bar(by_make, "make", "recall_count", "Recall volume by brand"))

    by_component = df.groupby("component", as_index=False)["recall_count"].sum().sort_values("recall_count", ascending=False)
    st.pyplot(chart_bar(by_component, "component", "recall_count", "Recall volume by component"))

    by_year = df.groupby("year", as_index=False)["recall_count"].sum().sort_values("year")
    st.pyplot(chart_line(by_year, "year", "recall_count", "Recall trend over time"))
    st.dataframe(df.head(25), width="stretch")

st.markdown("---")
st.caption("Portfolio integration: EU Vehicle Registration, EV Adoption & Charging, Fleet Telemetry, Used Car Price, and Vehicle Safety Recall Analysis")
