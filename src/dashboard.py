"""
Streamlit dashboard for EU Vehicle Registration ETL pipeline.
Inspired by The Python Graph Gallery visualization patterns.

Run: python -m streamlit run src/dashboard.py
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Page config
st.set_page_config(page_title="EU Vehicle Registration Dashboard", layout="wide")

# Set matplotlib style for gallery-like aesthetics
plt.style.use('seaborn-v0_8-whitegrid')

# Title
st.title("🚗 EU Vehicle Registration Dashboard")
st.markdown("Monitoring new vehicle registrations by country and power type (electric, hybrid, combustion)")

# Load or generate data
PROCESSED_DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"
csv_path = PROCESSED_DATA_DIR / "road_eqr_carpda_clean.csv"

try:
    df = pd.read_csv(csv_path)
    if len(df) <= 1:
        st.warning("⚠️ Cleaned data too small. Showing **demo data** for visualization purposes.")
        # Generate demo data for showcase
        countries = ["Germany", "France", "Italy", "Spain", "Netherlands", "Belgium", "Poland"]
        power_types = ["Combustion", "Hybrid", "Electric"]
        years = [2021, 2022, 2023, 2024, 2025]
        
        demo_data = []
        for country in countries:
            for power in power_types:
                for year in years:
                    base = np.random.randint(50000, 200000)
                    if power == "Electric":
                        trend = base * (1 + (year - 2021) * 0.15)  # 15% growth per year
                    elif power == "Hybrid":
                        trend = base * (1 + (year - 2021) * 0.08)  # 8% growth
                    else:
                        trend = base * (1 - (year - 2021) * 0.05)  # -5% decline
                    demo_data.append({
                        "country": country,
                        "power_type": power,
                        "year": year,
                        "registrations": max(int(trend), 1000)
                    })
        
        df = pd.DataFrame(demo_data)
        demo_mode = True
    else:
        demo_mode = False
except FileNotFoundError:
    st.error(f"❌ Data file not found: {csv_path}")
    st.info("Run `python src/extract.py && python src/transform.py` first.")
    st.stop()

# Sidebar filters
st.sidebar.header("Filters")
if "country" in df.columns:
    selected_countries = st.sidebar.multiselect(
        "Select Countries",
        df["country"].unique() if "country" in df.columns else [],
        default=df["country"].unique()[:3] if "country" in df.columns else []
    )
    if selected_countries:
        df_filtered = df[df["country"].isin(selected_countries)].copy()
    else:
        df_filtered = df.copy()
else:
    df_filtered = df.copy()

# --- KPI CARDS ---
st.subheader("📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if "registrations" in df_filtered.columns:
        total = df_filtered["registrations"].sum()
        st.metric("Total Registrations", f"{total:,.0f}")

with col2:
    if "country" in df_filtered.columns:
        st.metric("Countries Tracked", df_filtered["country"].nunique())

with col3:
    if "power_type" in df_filtered.columns:
        st.metric("Power Types", df_filtered["power_type"].nunique())

with col4:
    if "year" in df_filtered.columns:
        st.metric("Years Covered", f"{df_filtered['year'].min()}-{df_filtered['year'].max()}")

# --- CHART 1: Line Chart (Trend over time) ---
st.subheader("📈 Registration Trends by Power Type")
if "year" in df_filtered.columns and "power_type" in df_filtered.columns and "registrations" in df_filtered.columns:
    trend_data = df_filtered.groupby(["year", "power_type"])["registrations"].sum().reset_index()
    
    fig, ax = plt.subplots(figsize=(12, 5), dpi=100)
    
    for power in trend_data["power_type"].unique():
        subset = trend_data[trend_data["power_type"] == power]
        ax.plot(subset["year"], subset["registrations"], marker='o', linewidth=2.5, label=power, markersize=8)
    
    ax.set_xlabel("Year", fontweight='bold', fontsize=11)
    ax.set_ylabel("Number of Registrations", fontweight='bold', fontsize=11)
    ax.legend(frameon=True, fancybox=True, shadow=True)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
else:
    st.info("Columns for trend chart not found in data.")

# --- CHART 2: Grouped Bar Chart (by Country & Power Type) ---
st.subheader("🏆 Latest Year: Registrations by Country & Power Type")
if "country" in df_filtered.columns and "power_type" in df_filtered.columns and "registrations" in df_filtered.columns and "year" in df_filtered.columns:
    latest_year = df_filtered["year"].max()
    latest_data = df_filtered[df_filtered["year"] == latest_year]
    
    pivot_data = latest_data.pivot_table(
        index="country",
        columns="power_type",
        values="registrations",
        fill_value=0
    )
    
    fig, ax = plt.subplots(figsize=(12, 6), dpi=100)
    
    bar_width = 0.25
    x = np.arange(len(pivot_data.index))
    colors = ['#7f6d5f', '#557f2d', '#2d7f5e']
    
    for i, col in enumerate(pivot_data.columns):
        ax.bar(x + i * bar_width, pivot_data[col], bar_width, label=col, color=colors[i % len(colors)], edgecolor='white')
    
    ax.set_xlabel("Country", fontweight='bold', fontsize=11)
    ax.set_ylabel("Registrations", fontweight='bold', fontsize=11)
    ax.set_xticks(x + bar_width)
    ax.set_xticklabels(pivot_data.index, rotation=45, ha='right')
    ax.legend(frameon=True, fancybox=True, shadow=True)
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    st.pyplot(fig)
else:
    st.info("Grouped bar chart data not available.")

# --- CHART 3: Heatmap (Country × Power Type) ---
st.subheader("🔥 Heatmap: Registration Intensity by Country & Power Type")
if "country" in df_filtered.columns and "power_type" in df_filtered.columns and "registrations" in df_filtered.columns:
    heatmap_data = df_filtered.pivot_table(
        index="country",
        columns="power_type",
        values="registrations",
        aggfunc="sum",
        fill_value=0
    )
    
    fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
    im = ax.imshow(heatmap_data.values, cmap='YlOrRd', aspect='auto')
    ax.set_xticks(np.arange(len(heatmap_data.columns)))
    ax.set_yticks(np.arange(len(heatmap_data.index)))
    ax.set_xticklabels(heatmap_data.columns)
    ax.set_yticklabels(heatmap_data.index)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    
    # Add text annotations
    for i in range(len(heatmap_data.index)):
        for j in range(len(heatmap_data.columns)):
            text = ax.text(j, i, f'{int(heatmap_data.values[i, j])}',
                          ha="center", va="center", color="black", fontsize=9)
    
    ax.set_title("Total Registrations by Country & Power Type", fontweight='bold', fontsize=12, pad=15)
    cbar = plt.colorbar(im, ax=ax, label='Total Registrations')
    plt.tight_layout()
    st.pyplot(fig)
else:
    st.info("Heatmap data not available.")

# --- CHART 4: Stacked Area Chart (Composition over time) ---
st.subheader("📊 Market Composition Over Time")
if "year" in df_filtered.columns and "power_type" in df_filtered.columns and "registrations" in df_filtered.columns:
    area_data = df_filtered.groupby(["year", "power_type"])["registrations"].sum().reset_index()
    area_pivot = area_data.pivot_table(index="year", columns="power_type", values="registrations", fill_value=0)
    
    fig, ax = plt.subplots(figsize=(12, 5), dpi=100)
    
    ax.stackplot(
        area_pivot.index,
        area_pivot.T.values,
        labels=area_pivot.columns,
        alpha=0.8,
        colors=['#7f6d5f', '#557f2d', '#2d7f5e']
    )
    
    ax.set_xlabel("Year", fontweight='bold', fontsize=11)
    ax.set_ylabel("Total Registrations", fontweight='bold', fontsize=11)
    ax.legend(loc='upper left', frameon=True, fancybox=True, shadow=True)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
else:
    st.info("Area chart data not available.")

# --- DATA TABLE ---
st.subheader("📋 Raw Data")
st.dataframe(df_filtered.sort_values(by=df_filtered.columns[0], ascending=False), use_container_width=True)

# --- FOOTER ---
if demo_mode:
    st.info("**📌 Demo Mode**: Showing sample data for visualization. Connect real data to see live insights.")

st.markdown("---")
st.caption("EU Vehicle Registration ETL Pipeline | Powered by Streamlit 🚀")
