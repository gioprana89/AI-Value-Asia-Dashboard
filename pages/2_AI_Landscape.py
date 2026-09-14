
import streamlit as st
import plotly.express as px
from utils.data_loader import load_ai_company
from utils.styles import apply_style, header, footer
from utils.calculations import coverage_pct

st.set_page_config(page_title="AI Landscape | Asia", page_icon="🤖", layout="wide")
apply_style()
ai = load_ai_company()

header(
    "Asian AI Landscape",
    "Explore Bloomberg Intelligence Artificial Intelligence-theme companies by country, industry, value-chain exposure and assessment strength."
)

with st.sidebar:
    st.markdown("### Filters")
    countries = sorted(ai["country_name"].dropna().unique().tolist())
    country_sel = st.multiselect("Country", countries, default=countries)

    industries = sorted(ai["industry"].dropna().unique().tolist())
    industry_sel = st.multiselect("Industry", industries, default=industries)

    categories = sorted(ai["exposure_category"].dropna().unique().tolist())
    cat_sel = st.multiselect("AI exposure category", categories, default=categories)

    cap_groups = sorted(ai["market_cap_group"].dropna().unique().tolist())
    cap_sel = st.multiselect("Market-cap group", cap_groups, default=cap_groups)

f = ai[
    ai["country_name"].isin(country_sel)
    & ai["industry"].isin(industry_sel)
    & ai["exposure_category"].isin(cat_sel)
    & ai["market_cap_group"].isin(cap_sel)
].copy()

c1,c2,c3,c4 = st.columns(4)
c1.metric("Filtered AI firms", f"{f['security_key'].nunique():,}")
c2.metric("Countries", f"{f['country_name'].nunique():,}")
c3.metric("Mean AI strength", "—" if f.empty else f"{f['ai_composite_strength'].mean():.2f}")
c4.metric("ESG coverage", "—" if f.empty else f"{coverage_pct(f['esg_disclosure_score']):.1f}%")

left,right = st.columns([1,1])
with left:
    by_country = f.groupby("country_name",as_index=False).size().rename(columns={"size":"companies"})
    fig=px.bar(
        by_country.sort_values("companies"), x="companies", y="country_name",
        orientation="h", title="AI firms by country",
        labels={"companies":"Companies","country_name":""}
    )
    fig.update_layout(height=400, margin=dict(l=10,r=10,t=55,b=10))
    st.plotly_chart(fig,use_container_width=True)

with right:
    by_cat = f.groupby("exposure_category",as_index=False).size().rename(columns={"size":"companies"})
    fig=px.bar(
        by_cat.sort_values("companies"), x="companies", y="exposure_category",
        orientation="h", title="AI value-chain exposure",
        labels={"companies":"Companies","exposure_category":""}
    )
    fig.update_layout(height=400, margin=dict(l=10,r=10,t=55,b=10))
    st.plotly_chart(fig,use_container_width=True)

left,right = st.columns([1,1])
with left:
    fig=px.histogram(
        f, x="ai_composite_strength", nbins=8,
        title="Distribution of composite AI strength",
        labels={"ai_composite_strength":"Composite AI strength","count":"Companies"}
    )
    fig.update_layout(height=380, margin=dict(l=10,r=10,t=55,b=10))
    st.plotly_chart(fig,use_container_width=True)

with right:
    fig=px.scatter(
        f, x="ai_revenue_strength", y="ai_theme_strength",
        hover_name="company", hover_data=["country_name","industry","exposure_category","market_cap_group"],
        title="Revenue strength vs theme strength",
        labels={
            "ai_revenue_strength":"AI revenue strength",
            "ai_theme_strength":"AI theme strength"
        }
    )
    fig.update_xaxes(range=[0.5,3.5], dtick=1)
    fig.update_yaxes(range=[0.5,3.5], dtick=1)
    fig.update_layout(height=380, margin=dict(l=10,r=10,t=55,b=10))
    st.plotly_chart(fig,use_container_width=True)

st.subheader("Company ranking")
rank = f.sort_values(
    ["ai_composite_strength","esg_disclosure_score"],
    ascending=[False,False]
).copy()
rank.insert(0, "rank", range(1, len(rank)+1))
st.dataframe(
    rank[[
        "rank","company","country_name","industry","exposure_category","market_cap_group",
        "revenue_assessment","theme_assessment","ai_composite_strength","esg_disclosure_score"
    ]],
    use_container_width=True,
    hide_index=True,
)

st.download_button(
    "Download filtered AI companies (CSV)",
    data=rank.to_csv(index=False).encode("utf-8"),
    file_name="filtered_ai_companies.csv",
    mime="text/csv"
)

footer()
