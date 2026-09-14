
import streamlit as st
import plotly.express as px
from utils.data_loader import load_all
from utils.styles import apply_style, header, footer
from utils.calculations import coverage_pct, get_ai_country_counts, get_ai_industry_counts

st.set_page_config(
    page_title="AI Capability & Financial Value in Asia",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_style()

company_master, ai_df, fin_df, quality = load_all()

header(
    "AI Capability & Financial Value in Asia",
    "Executive overview of Bloomberg Intelligence AI exposure, ESG coverage, and the current financial-data universe."
)

ai_count = ai_df["security_key"].nunique()
country_count = ai_df["country_name"].nunique()
industry_count = ai_df["industry"].nunique()
esg_coverage = coverage_pct(ai_df["esg_disclosure_score"])
fin_companies = fin_df["security_key"].nunique()
fin_obs = len(fin_df)
overlap = len(set(ai_df["security_key"]).intersection(set(fin_df["security_key"])))

c1,c2,c3,c4 = st.columns(4)
c1.metric("AI companies", f"{ai_count:,}")
c2.metric("Countries represented", f"{country_count:,}")
c3.metric("Industries", f"{industry_count:,}")
c4.metric("AI firms with ESG data", f"{esg_coverage:.1f}%")

c5,c6,c7 = st.columns(3)
c5.metric("Financial-panel companies", f"{fin_companies:,}")
c6.metric("Financial firm-years", f"{fin_obs:,}")
c7.metric("AI–financial overlap", f"{overlap:,}")

if overlap == 0:
    st.markdown(
        '<div class="notice"><b>Research validity guardrail:</b> the current financial panel has '
        'no company overlap with the AI-theme sample. Relationship charts (AI → resilience → firm value) '
        'must remain disabled until Bloomberg financial history is collected for the AI firms.</div>',
        unsafe_allow_html=True,
    )

left, right = st.columns([1,1])
with left:
    country = get_ai_country_counts(ai_df)
    fig = px.bar(
        country.sort_values("ai_companies"),
        x="ai_companies", y="country_name",
        orientation="h",
        labels={"ai_companies":"AI companies","country_name":""},
        title="AI companies by country",
    )
    fig.update_layout(height=390, margin=dict(l=10,r=10,t=55,b=10))
    st.plotly_chart(fig, use_container_width=True)

with right:
    industry = get_ai_industry_counts(ai_df)
    fig = px.bar(
        industry.sort_values("ai_companies"),
        x="ai_companies", y="industry",
        orientation="h",
        labels={"ai_companies":"AI companies","industry":""},
        title="AI companies by industry",
    )
    fig.update_layout(height=390, margin=dict(l=10,r=10,t=55,b=10))
    st.plotly_chart(fig, use_container_width=True)

left, right = st.columns([1,1])
with left:
    cap = (
        ai_df.groupby("market_cap_group", as_index=False)
        .size().rename(columns={"size":"companies"})
        .sort_values("companies", ascending=False)
    )
    fig = px.bar(
        cap, x="market_cap_group", y="companies",
        labels={"market_cap_group":"Market-cap group","companies":"Companies"},
        title="AI companies by market-cap group",
    )
    fig.update_layout(height=360, margin=dict(l=10,r=10,t=55,b=10))
    st.plotly_chart(fig, use_container_width=True)

with right:
    strength = (
        ai_df.groupby("country_name", as_index=False)["ai_composite_strength"]
        .mean().sort_values("ai_composite_strength", ascending=False)
    )
    fig = px.bar(
        strength, x="country_name", y="ai_composite_strength",
        labels={"country_name":"","ai_composite_strength":"Composite AI strength"},
        title="Average AI exposure strength by country",
    )
    fig.update_yaxes(range=[0,3.1])
    fig.update_layout(height=360, margin=dict(l=10,r=10,t=55,b=10))
    st.plotly_chart(fig, use_container_width=True)

with st.expander("How the AI strength metric is constructed"):
    st.write(
        "Bloomberg's raw Revenue Assessment and Theme Assessment use lower values for stronger "
        "thematic relevance. This dashboard keeps the raw Bloomberg fields and creates transparent "
        "reverse-coded strengths: Revenue Strength = 4 − Revenue Assessment; Theme Strength = "
        "4 − Theme Assessment; Composite AI Strength = average of the two. Higher dashboard values "
        "therefore mean stronger AI exposure."
    )

st.subheader("AI company table")
table_cols = [
    "company","country_name","industry","exposure_category","market_cap_group",
    "revenue_assessment","theme_assessment","ai_composite_strength","esg_disclosure_score"
]
st.dataframe(
    ai_df[table_cols].sort_values(["country_name","company"]),
    use_container_width=True,
    hide_index=True,
)

footer()
