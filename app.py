import streamlit as st
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
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/world_happiness.csv")
    return df

df = load_data()

# -----------------------------
# CLEAN DATA
# -----------------------------
df = df.dropna()

# -----------------------------
# SAFE COLUMN DETECTION FUNCTION
# -----------------------------
def get_col(df, options):
    for col in options:
        if col in df.columns:
            return df[col]
    return None

# -----------------------------
# MAP COLUMNS SAFELY
# -----------------------------
df["Country"] = get_col(df, ["Country name", "Country"])
df["GDP"] = get_col(df, ["Log GDP per capita", "GDP per capita"])
df["Health"] = get_col(df, ["Healthy life expectancy"])
df["Freedom"] = get_col(df, ["Freedom to make life choices"])
df["Social Support"] = get_col(df, ["Social support"])
df["Generosity"] = get_col(df, ["Generosity"])
df["Corruption"] = get_col(df, ["Perceptions of corruption"])
df["Happiness Score"] = get_col(df, ["Life Ladder", "Happiness score", "Happiness Score"])

# -----------------------------
# VALIDATION CHECK
# -----------------------------
required = ["Country", "GDP", "Health", "Freedom", "Social Support", "Happiness Score"]

if any(df[col] is None for col in required):
    st.error("❌ Dataset columns do not match expected World Happiness format.")
    st.stop()

# -----------------------------
# QoL SCORE
# -----------------------------
df["QoL Score"] = (
    df["Happiness Score"] * 0.30 +
    df["GDP"] * 0.20 +
    df["Health"] * 0.15 +
    df["Freedom"] * 0.15 +
    df["Social Support"] * 0.10 +
    df["Generosity"].fillna(0) * 0.05 +
    df["Corruption"].fillna(0) * 0.05
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

    st.header("📊 Overview Dashboard")

    col1, col2, col3 = st.columns(3)

    col1.metric("Countries", df["Country"].nunique())
    col2.metric("Avg QoL Score", round(df["QoL Score"].mean(), 2))
    col3.metric("Records", len(df))

    st.subheader("Dataset Preview")
    st.dataframe(df.head(20))

# -----------------------------
# COUNTRY COMPARISON
# -----------------------------
elif page == "Country Comparison":

    st.header("⚖️ Compare Countries")

    countries = sorted(df["Country"].dropna().unique())

    c1 = st.selectbox("Country 1", countries)
    c2 = st.selectbox("Country 2", countries, index=1)

    compare_df = df[df["Country"].isin([c1, c2])]

    st.dataframe(compare_df)

# -----------------------------
# TOP RANKINGS
# -----------------------------
elif page == "Top Rankings":

    st.header("🏆 Top 10 Countries")

    top10 = df.sort_values("QoL Score", ascending=False).head(10)

    st.dataframe(top10)

    fig = px.bar(
        top10,
        x="Country",
        y="QoL Score",
        title="Top 10 Countries by Quality of Life"
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# ANALYTICS
# -----------------------------
elif page == "Analytics":

    st.header("📈 Analytics Dashboard")

    st.subheader("GDP vs Happiness")

    fig1 = px.scatter(
        df,
        x="GDP",
        y="Happiness Score",
        hover_name="Country"
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Freedom vs Happiness")

    fig2 = px.scatter(
        df,
        x="Freedom",
        y="Happiness Score",
        hover_name="Country"
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Correlation Matrix")

    numeric_df = df.select_dtypes(include="number")
    corr = numeric_df.corr()

    fig3 = px.imshow(
        corr,
        text_auto=True,
        title="Correlation Matrix"
    )
    st.plotly_chart(fig3, use_container_width=True)