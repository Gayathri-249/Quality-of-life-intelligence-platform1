import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# PAGE CONFIGURATION
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
    df = pd.read_csv("data/world_happiness.csv")
    return df

df = load_data()

# -----------------------------
# CLEANING (PANDAS ONLY)
# -----------------------------
df = df[[col for col in df.columns if not str(col).startswith("_duplicated")]]
df = df.dropna()

# -----------------------------
# SAFE COLUMN CHECK (avoids crashes)
# -----------------------------
required_columns = [
    "Country name",
    "Log GDP per capita",
    "Social support",
    "Healthy life expectancy",
    "Freedom to make life choices",
    "Generosity",
    "Perceptions of corruption",
    "Life Ladder"
]

for col in required_columns:
    if col not in df.columns:
        st.error(f"Missing column in dataset: {col}")
        st.stop()

# -----------------------------
# CREATE STANDARDIZED COLUMNS
# -----------------------------
df["Country"] = df["Country name"]
df["GDP"] = df["Log GDP per capita"]
df["Social Support"] = df["Social support"]
df["Health"] = df["Healthy life expectancy"]
df["Freedom"] = df["Freedom to make life choices"]
df["Generosity"] = df["Generosity"]
df["Corruption"] = df["Perceptions of corruption"]
df["Happiness Score"] = df["Life Ladder"]

# -----------------------------
# QoL SCORE (PANDAS VERSION)
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

# -----------------------------
# SIDEBAR NAVIGATION
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

    total_countries = df["Country"].nunique()
    avg_qol = round(df["QoL Score"].mean(), 2)

    highest_country = df.sort_values("QoL Score", ascending=False).iloc[0]["Country"]
    lowest_country = df.sort_values("QoL Score", ascending=True).iloc[0]["Country"]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Countries", total_countries)
    col2.metric("Average QoL", avg_qol)
    col3.metric("Highest Country", highest_country)
    col4.metric("Lowest Country", lowest_country)

    st.subheader("Dataset Preview")
    st.dataframe(df)

# -----------------------------
# COUNTRY COMPARISON
# -----------------------------
elif page == "Country Comparison":

    st.header("Country Comparison")

    countries = sorted(df["Country"].unique())

    country1 = st.selectbox("Select Country 1", countries)
    country2 = st.selectbox("Select Country 2", countries, index=1)

    compare_df = df[df["Country"].isin([country1, country2])]

    st.dataframe(compare_df)

    comparison_columns = [
        "GDP", "Health", "Freedom",
        "Social Support", "Generosity",
        "Corruption", "Happiness Score", "QoL Score"
    ]

    radar_data = compare_df.set_index("Country")[comparison_columns]

    st.subheader("Comparison Table")
    st.dataframe(radar_data)

# -----------------------------
# TOP RANKINGS
# -----------------------------
elif page == "Top Rankings":

    st.header("Top Rankings")

    top10 = df.sort_values("QoL Score", ascending=False).head(10)

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

    fig1 = px.scatter(
        df,
        x="GDP",
        y="Happiness Score",
        hover_name="Country"
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Freedom vs Happiness Score")

    fig2 = px.scatter(
        df,
        x="Freedom",
        y="Happiness Score",
        hover_name="Country"
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Top 15 Countries")

    top15 = df.sort_values("QoL Score", ascending=False).head(15)

    fig3 = px.bar(
        top15,
        x="Country",
        y="QoL Score"
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Correlation Matrix")

    numeric_df = df.select_dtypes(include="number")
    corr = numeric_df.corr()

    fig4 = px.imshow(
        corr,
        text_auto=True,
        aspect="auto",
        title="Correlation Matrix"
    )

    st.plotly_chart(fig4, use_container_width=True)