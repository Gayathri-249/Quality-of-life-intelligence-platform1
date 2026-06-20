import streamlit as st
import pandas as pd
import plotly.express as px
import os

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
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    file_path = "data/world_happiness.csv"
    if not os.path.exists(file_path):
        return None
    return pd.read_csv(file_path)

df = load_data()

if df is None:
    st.error("❌ Dataset not found in data/world_happiness.csv")
    st.stop()

df = df.dropna()

# -----------------------------
# COLUMN RENAME (SAFE)
# -----------------------------
rename_map = {
    "Country name": "Country",
    "Life Ladder": "Happiness Score",
    "Explained by: Log GDP per capita": "GDP",
    "Explained by: Social support": "Social Support",
    "Explained by: Healthy life expectancy": "Health",
    "Freedom to make life choices": "Freedom",
    "Generosity": "Generosity",
    "Perceptions of corruption": "Corruption"
}

df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

# -----------------------------
# REQUIRED CHECK
# -----------------------------
if "Country" not in df.columns or "Happiness Score" not in df.columns:
    st.error("Missing required columns in dataset")
    st.stop()

# Fill missing optional columns
for col in ["GDP", "Social Support", "Health", "Freedom", "Generosity", "Corruption"]:
    if col not in df.columns:
        df[col] = 0

# -----------------------------
# QoL SCORE
# -----------------------------
df["QoL Score"] = (
    df["Happiness Score"] * 0.30 +
    df["GDP"] * 0.20 +
    df["Health"] * 0.15 +
    df["Freedom"] * 0.15 +
    df["Social Support"] * 0.10 +
    df["Generosity"] * 0.05 +
    df["Corruption"] * 0.05
)

pdf = df.copy()

# -----------------------------
# SIDEBAR MENU
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

    total_countries = pdf["Country"].nunique()
    avg_qol = round(pdf["QoL Score"].mean(), 2)

    top_country = pdf.sort_values("QoL Score", ascending=False).iloc[0]["Country"]
    low_country = pdf.sort_values("QoL Score", ascending=True).iloc[0]["Country"]

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Countries", total_countries)
    c2.metric("Average QoL", avg_qol)
    c3.metric("Highest Country", top_country)
    c4.metric("Lowest Country", low_country)

    st.subheader("Dataset Preview")
    st.dataframe(pdf)

# -----------------------------
# COUNTRY COMPARISON
# -----------------------------
elif page == "Country Comparison":

    st.header("Country Comparison")

    countries = sorted(pdf["Country"].unique())

    country1 = st.selectbox("Select Country 1", countries)
    country2 = st.selectbox("Select Country 2", countries, index=1)

    compare_df = pdf[pdf["Country"].isin([country1, country2])]

    st.dataframe(compare_df)

    cols = [
        "GDP", "Health", "Freedom",
        "Social Support", "Generosity",
        "Corruption", "Happiness Score", "QoL Score"
    ]

    cols = [c for c in cols if c in pdf.columns]

    st.subheader("Comparison Table")
    st.dataframe(compare_df[["Country"] + cols])

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
        title="Top 10 Countries by Quality of Life Score"
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# ANALYTICS
# -----------------------------
elif page == "Analytics":

    st.header("Analytics Dashboard")

    st.subheader("GDP vs Happiness Score")

    if "GDP" in pdf.columns:
        fig1 = px.scatter(
            pdf,
            x="GDP",
            y="Happiness Score",
            hover_name="Country"
        )
        st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Freedom vs Happiness Score")

    if "Freedom" in pdf.columns:
        fig2 = px.scatter(
            pdf,
            x="Freedom",
            y="Happiness Score",
            hover_name="Country"
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Top 15 Countries")

    top15 = pdf.sort_values("QoL Score", ascending=False).head(15)

    fig3 = px.bar(
        top15,
        x="Country",
        y="QoL Score"
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Correlation Matrix")

    numeric_df = pdf.select_dtypes(include=["number"])

    if not numeric_df.empty:
        corr = numeric_df.corr()

        fig4 = px.imshow(
            corr,
            text_auto=True,
            aspect="auto",
            title="Correlation Matrix"
        )

        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.warning("No numeric data available for correlation.")