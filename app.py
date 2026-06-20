import streamlit as st
import polars as pl
import pandas as pd
import plotly.express as px

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Quality of Life Intelligence Platform",
    layout="wide"
)

st.title("🌍 Quality of Life Intelligence Platform")

st.markdown("""
Compare countries using World Happiness Report indicators and analyze Quality of Life factors.
""")

# -----------------------------
# LOAD DATA (SAFE)
# -----------------------------
@st.cache_data
def load_data():
    try:
        return pl.read_csv("data/world_happiness.csv")
    except Exception as e:
        st.error(f"Data loading failed: {e}")
        return pl.DataFrame()

df = load_data()

if df.is_empty():
    st.stop()

# -----------------------------
# CLEANING
# -----------------------------
df = df.select([c for c in df.columns if c and not c.startswith("_duplicated")])
df = df.drop_nulls()

# -----------------------------
# SAFE COLUMN RENAME (ONLY IF EXISTS)
# -----------------------------
rename_map = {
    "Country name": "Country",
    "Life evaluation (3-year average)": "Happiness Score",
    "Explained by: Log GDP per capita": "GDP",
    "Explained by: Social support": "Social Support",
    "Explained by: Healthy life expectancy": "Health",
    "Explained by: Freedom to make life choices": "Freedom",
    "Explained by: Generosity": "Generosity",
    "Explained by: Perceptions of corruption": "Corruption"
}

existing_renames = {k: v for k, v in rename_map.items() if k in df.columns}
df = df.rename(existing_renames)

required_cols = [
    "Country", "Happiness Score", "GDP", "Social Support",
    "Health", "Freedom", "Generosity", "Corruption"
]

missing = [c for c in required_cols if c not in df.columns]

if missing:
    st.error(f"Missing required columns: {missing}")
    st.stop()

# -----------------------------
# QoL SCORE
# -----------------------------
df = df.with_columns(
    (
        pl.col("Happiness Score") * 0.30 +
        pl.col("GDP") * 0.20 +
        pl.col("Health") * 0.15 +
        pl.col("Freedom") * 0.15 +
        pl.col("Social Support") * 0.10 +
        pl.col("Generosity") * 0.05 +
        pl.col("Corruption") * 0.05
    ).alias("QoL Score")
)

pdf = df.to_pandas()

# -----------------------------
# SIDEBAR
# -----------------------------
page = st.sidebar.selectbox(
    "Navigation",
    ["Overview", "Country Comparison", "Top Rankings", "Analytics"]
)

# -----------------------------
# OVERVIEW
# -----------------------------
if page == "Overview":

    st.header("Project Overview")

    total_countries = len(pdf)
    avg_qol = round(pdf["QoL Score"].mean(), 2)

    highest_country = pdf.sort_values("QoL Score", ascending=False).iloc[0]["Country"]
    lowest_country = pdf.sort_values("QoL Score", ascending=True).iloc[0]["Country"]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Countries", total_countries)
    col2.metric("Average QoL", avg_qol)
    col3.metric("Highest Country", highest_country)
    col4.metric("Lowest Country", lowest_country)

    st.subheader("Dataset Preview")
    st.dataframe(pdf)

# -----------------------------
# COUNTRY COMPARISON
# -----------------------------
elif page == "Country Comparison":

    st.header("Country Comparison")

    countries = sorted(pdf["Country"].dropna().unique())

    country1 = st.selectbox("Select Country 1", countries)
    country2 = st.selectbox("Select Country 2", countries, index=1 if len(countries) > 1 else 0)

    compare_df = pdf[pdf["Country"].isin([country1, country2])]
    st.dataframe(compare_df)

    comparison_columns = [
        "GDP", "Health", "Freedom",
        "Social Support", "Generosity",
        "Corruption", "Happiness Score", "QoL Score"
    ]

    radar_data = compare_df.set_index("Country")[comparison_columns]
    st.subheader("Comparison Metrics")
    st.dataframe(radar_data)

# -----------------------------
# TOP RANKINGS
# -----------------------------
elif page == "Top Rankings":

    st.header("Top Rankings")

    top10 = pdf.sort_values("QoL Score", ascending=False).head(10)

    st.subheader("Top 10 Countries")
    st.dataframe(top10)

    fig = px.bar(
        top10,
        x="Country",
        y="QoL Score",
        title="Top 10 Countries by QoL Score"
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# ANALYTICS
# -----------------------------
elif page == "Analytics":

    st.header("Analytics Dashboard")

    st.subheader("GDP vs Happiness Score")
    fig1 = px.scatter(pdf, x="GDP", y="Happiness Score", hover_name="Country")
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Freedom vs Happiness Score")
    fig2 = px.scatter(pdf, x="Freedom", y="Happiness Score", hover_name="Country")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Top 15 Countries")

    top15 = pdf.sort_values("QoL Score", ascending=False).head(15)

    fig3 = px.bar(top15, x="Country", y="QoL Score")
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Correlation Matrix")

    numeric_df = pdf.select_dtypes(include="number")

    if numeric_df.shape[1] > 1:
        corr = numeric_df.corr()

        fig4 = px.imshow(
            corr,
            text_auto=True,
            aspect="auto",
            title="Correlation Matrix"
        )

        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.warning("Not enough numeric columns for correlation matrix.")