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
st.markdown("Compare countries using World Happiness Report indicators.")

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/world_happiness.csv")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# -----------------------------
# SAFE COLUMN DETECTION
# -----------------------------
def find_col(possible_names):
    for name in possible_names:
        if name in df.columns:
            return name
    return None

country_col = find_col(["Country name", "Country"])
happiness_col = find_col(["Life Ladder", "Ladder score"])
gdp_col = find_col(["Log GDP per capita", "Logged GDP per capita"])
social_col = find_col(["Social support"])
health_col = find_col(["Healthy life expectancy at birth", "Healthy life expectancy"])
freedom_col = find_col(["Freedom to make life choices"])
generosity_col = find_col(["Generosity"])
corruption_col = find_col(["Perceptions of corruption"])

# -----------------------------
# VALIDATION (PREVENT CRASH)
# -----------------------------
required = [country_col, happiness_col, gdp_col]

if None in required:
    st.error("❌ Dataset format not recognized. Please check your CSV columns.")
    st.write("Detected columns:", df.columns)
    st.stop()

# -----------------------------
# CLEAN DATA
# -----------------------------
df_clean = pd.DataFrame()

df_clean["Country"] = df[country_col]
df_clean["Happiness"] = pd.to_numeric(df[happiness_col], errors="coerce")
df_clean["GDP"] = pd.to_numeric(df[gdp_col], errors="coerce")

if social_col:
    df_clean["Social Support"] = pd.to_numeric(df[social_col], errors="coerce")
else:
    df_clean["Social Support"] = 0

if health_col:
    df_clean["Health"] = pd.to_numeric(df[health_col], errors="coerce")
else:
    df_clean["Health"] = 0

if freedom_col:
    df_clean["Freedom"] = pd.to_numeric(df[freedom_col], errors="coerce")
else:
    df_clean["Freedom"] = 0

if generosity_col:
    df_clean["Generosity"] = pd.to_numeric(df[generosity_col], errors="coerce")
else:
    df_clean["Generosity"] = 0

if corruption_col:
    df_clean["Corruption"] = pd.to_numeric(df[corruption_col], errors="coerce")
else:
    df_clean["Corruption"] = 0

df_clean = df_clean.dropna()

# -----------------------------
# QoL SCORE (SAFE)
# -----------------------------
df_clean["QoL Score"] = (
    df_clean["Happiness"] * 0.30 +
    df_clean["GDP"] * 0.20 +
    df_clean["Health"] * 0.15 +
    df_clean["Freedom"] * 0.15 +
    df_clean["Social Support"] * 0.10 +
    df_clean["Generosity"] * 0.05 +
    df_clean["Corruption"] * 0.05
)

pdf = df_clean.copy()

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

    st.header("📊 Overview Dashboard")

    col1, col2, col3 = st.columns(3)

    col1.metric("Countries", len(pdf))
    col2.metric("Avg QoL", round(pdf["QoL Score"].mean(), 2) if len(pdf) else 0)
    col3.metric("Max QoL", round(pdf["QoL Score"].max(), 2) if len(pdf) else 0)

    st.subheader("Dataset Preview")
    st.dataframe(pdf.head(50))

# -----------------------------
# COUNTRY COMPARISON
# -----------------------------
elif page == "Country Comparison":

    st.header("🌍 Country Comparison")

    if len(pdf) == 0:
        st.warning("No data available")
        st.stop()

    countries = sorted(pdf["Country"].unique())

    c1 = st.selectbox("Country 1", countries)
    c2 = st.selectbox("Country 2", countries, index=1)

    compare_df = pdf[pdf["Country"].isin([c1, c2])]
    st.dataframe(compare_df)

    st.subheader("Metrics Comparison")

    st.dataframe(compare_df.set_index("Country")[[
        "GDP", "Health", "Freedom",
        "Social Support", "Generosity",
        "Corruption", "Happiness", "QoL Score"
    ]])

# -----------------------------
# TOP RANKINGS
# -----------------------------
elif page == "Top Rankings":

    st.header("🏆 Top 10 Countries")

    top10 = pdf.sort_values("QoL Score", ascending=False).head(10)

    st.dataframe(top10)

    fig = px.bar(
        top10,
        x="Country",
        y="QoL Score",
        title="Top 10 Countries by QoL"
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# ANALYTICS
# -----------------------------
elif page == "Analytics":

    st.header("📈 Analytics Dashboard")

    fig1 = px.scatter(
        pdf,
        x="GDP",
        y="Happiness",
        hover_name="Country",
        title="GDP vs Happiness"
    )
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.scatter(
        pdf,
        x="Freedom",
        y="Happiness",
        hover_name="Country",
        title="Freedom vs Happiness"
    )
    st.plotly_chart(fig2, use_container_width=True)

    top15 = pdf.sort_values("QoL Score", ascending=False).head(15)

    fig3 = px.bar(
        top15,
        x="Country",
        y="QoL Score",
        title="Top 15 Countries"
    )
    st.plotly_chart(fig3, use_container_width=True)

    corr = pdf[[
        "GDP", "Health", "Freedom",
        "Social Support", "Generosity",
        "Corruption", "Happiness", "QoL Score"
    ]].corr()

    fig4 = px.imshow(
        corr,
        text_auto=True,
        title="Correlation Matrix"
    )

    st.plotly_chart(fig4, use_container_width=True)