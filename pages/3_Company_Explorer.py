import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

from utils.data_loader import load_ai_company, load_financial_panel
from utils.styles import apply_style, header, footer

st.set_page_config(
    page_title="Company Explorer | Bloomberg AI Dashboard",
    page_icon="🏢",
    layout="wide",
)
apply_style()

ai = load_ai_company()
fin = load_financial_panel()

header(
    "Company Explorer",
    "Drill down into one company at a time without mixing the current AI sample and the separate financial-history sample."
)

mode = st.radio(
    "Explorer mode",
    ["AI Company Profile", "Financial Panel Profile"],
    horizontal=True,
)


def safe_text(value):
    if pd.isna(value) or str(value).strip() in {"", "nan", "None"}:
        return "—"
    return str(value)


def percentile_rank(series, value):
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty or pd.isna(value):
        return np.nan
    return 100.0 * (s <= value).mean()


if mode == "AI Company Profile":
    st.caption(
        "This mode uses Bloomberg Intelligence Artificial Intelligence-theme companies. "
        "Financial relationship metrics are shown only if that same company exists in the current financial panel."
    )

    countries = sorted(ai["country_name"].dropna().unique().tolist())
    selected_country = st.selectbox("Country", ["All countries"] + countries)

    pool = ai.copy()
    if selected_country != "All countries":
        pool = pool[pool["country_name"].eq(selected_country)]

    companies = sorted(pool["company"].dropna().unique().tolist())
    if not companies:
        st.warning("No AI companies match the selected country.")
        footer()
        st.stop()

    selected_company = st.selectbox("Select AI company", companies)
    row = pool[pool["company"].eq(selected_company)].iloc[0]

    st.markdown("### Company profile")
    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Country", safe_text(row["country_name"]))
    p2.metric("Industry", safe_text(row["industry"]))
    p3.metric("AI exposure category", safe_text(row["exposure_category"]))
    p4.metric("Market-cap group", safe_text(row["market_cap_group"]))

    st.markdown("### AI assessment")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Revenue assessment (raw)", safe_text(row["revenue_assessment"]))
    c2.metric("Theme assessment (raw)", safe_text(row["theme_assessment"]))
    c3.metric("Composite AI strength", "—" if pd.isna(row["ai_composite_strength"]) else f"{row['ai_composite_strength']:.2f}")
    c4.metric("ESG disclosure score", "—" if pd.isna(row["esg_disclosure_score"]) else f"{row['esg_disclosure_score']:.2f}")

    st.info(
        "Bloomberg raw AI assessments use lower values for stronger thematic exposure. "
        "The dashboard reverse-codes them so a higher AI strength value means stronger exposure."
    )

    # Peer comparison definition
    peer_mode = st.selectbox(
        "Peer comparison",
        ["Same country", "Same industry", "Same market-cap group", "All AI firms"],
    )
    if peer_mode == "Same country":
        peers = ai[ai["country_name"].eq(row["country_name"])].copy()
    elif peer_mode == "Same industry":
        peers = ai[ai["industry"].eq(row["industry"])].copy()
    elif peer_mode == "Same market-cap group":
        peers = ai[ai["market_cap_group"].eq(row["market_cap_group"])].copy()
    else:
        peers = ai.copy()

    ai_pct = percentile_rank(peers["ai_composite_strength"], row["ai_composite_strength"])
    esg_pct = percentile_rank(peers["esg_disclosure_score"], row["esg_disclosure_score"])

    st.markdown("### Peer position")
    q1, q2, q3 = st.columns(3)
    q1.metric("Peer companies", f"{peers['security_key'].nunique():,}")
    q2.metric("AI-strength percentile", "—" if pd.isna(ai_pct) else f"{ai_pct:.0f}th")
    q3.metric("ESG percentile", "—" if pd.isna(esg_pct) else f"{esg_pct:.0f}th")

    plot_df = peers[["company", "ai_composite_strength", "esg_disclosure_score", "country_name", "industry"]].copy()
    fig = px.scatter(
        plot_df,
        x="ai_composite_strength",
        y="esg_disclosure_score",
        hover_name="company",
        hover_data=["country_name", "industry"],
        title=f"AI strength vs ESG disclosure — {peer_mode.lower()}",
        labels={
            "ai_composite_strength": "Composite AI strength",
            "esg_disclosure_score": "ESG disclosure score",
        },
    )
    fig.add_scatter(
        x=[row["ai_composite_strength"]],
        y=[row["esg_disclosure_score"]],
        mode="markers+text",
        text=[selected_company],
        textposition="top center",
        marker=dict(size=15, symbol="diamond"),
        name="Selected company",
    )
    fig.update_layout(height=480, margin=dict(l=10, r=10, t=55, b=10))
    st.plotly_chart(fig, use_container_width=True)

    # AI raw and transformed detail table
    detail = pd.DataFrame({
        "Metric": [
            "Bloomberg Revenue Assessment",
            "Bloomberg Theme Assessment",
            "Bloomberg Total Assessment",
            "Dashboard Revenue Strength",
            "Dashboard Theme Strength",
            "Dashboard Composite AI Strength",
        ],
        "Value": [
            row["revenue_assessment"],
            row["theme_assessment"],
            row["total_assessment"],
            row["ai_revenue_strength"],
            row["ai_theme_strength"],
            row["ai_composite_strength"],
        ]
    })
    st.dataframe(detail, use_container_width=True, hide_index=True)

    # Only show financial history if this company genuinely overlaps
    company_fin = fin[fin["security_key"].eq(row["security_key"])].copy()
    st.markdown("### Financial history availability")
    if company_fin.empty:
        st.warning(
            "No matching financial-history rows exist for this AI company in the current workbook. "
            "This is why V1 does not yet show AI → financial resilience → firm value for this company."
        )
    else:
        st.success(f"{len(company_fin)} fiscal-year observations are available for this AI company.")
        metrics = {
            "Tobin's Q": "tobins_q",
            "ROA": "roa",
            "Bloomberg ESG Score": "besg_esg_score",
            "Market Capitalization": "market_cap",
            "Current Ratio": "current_ratio",
            "Interest Coverage": "net_interest_coverage",
        }
        metric_label = st.selectbox("Financial metric", list(metrics))
        metric = metrics[metric_label]
        plot = company_fin.dropna(subset=[metric]).sort_values("fiscal_year")
        fig = px.line(plot, x="fiscal_year", y=metric, markers=True, title=f"{selected_company}: {metric_label}")
        fig.update_layout(height=420, margin=dict(l=10, r=10, t=55, b=10))
        st.plotly_chart(fig, use_container_width=True)

else:
    st.caption(
        "This mode explores the companies for which the current workbook already contains annual financial history. "
        "It does not imply these firms are part of the Bloomberg AI-theme sample."
    )

    countries = sorted(fin["country_name"].dropna().unique().tolist())
    selected_country = st.selectbox("Country", ["All countries"] + countries)
    pool = fin.copy()
    if selected_country != "All countries":
        pool = pool[pool["country_name"].eq(selected_country)]

    company_options = (
        pool[["security_key", "company"]]
        .drop_duplicates()
        .sort_values("company")
    )
    company_label_to_key = dict(zip(company_options["company"], company_options["security_key"]))
    selected_company = st.selectbox("Select financial-panel company", list(company_label_to_key))
    selected_key = company_label_to_key[selected_company]
    company_fin = fin[fin["security_key"].eq(selected_key)].sort_values("fiscal_year").copy()

    min_year = int(company_fin["fiscal_year"].min())
    max_year = int(company_fin["fiscal_year"].max())
    year_range = st.slider("Fiscal-year range", min_year, max_year, (min_year, max_year))
    company_fin = company_fin[company_fin["fiscal_year"].between(year_range[0], year_range[1])]

    st.markdown("### Company profile")
    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Company", selected_company)
    p2.metric("Country", safe_text(company_fin["country_name"].iloc[0]) if not company_fin.empty else "—")
    p3.metric("Firm-year observations", f"{len(company_fin):,}")
    p4.metric("Year span", f"{year_range[0]}–{year_range[1]}")

    latest = company_fin.sort_values("fiscal_year").iloc[-1] if not company_fin.empty else None
    if latest is not None:
        st.markdown("### Latest available snapshot")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Tobin's Q", "—" if pd.isna(latest["tobins_q"]) else f"{latest['tobins_q']:.2f}")
        c2.metric("ROA", "—" if pd.isna(latest["roa"]) else f"{latest['roa']:.2f}")
        c3.metric("Bloomberg ESG Score", "—" if pd.isna(latest["besg_esg_score"]) else f"{latest['besg_esg_score']:.2f}")
        c4.metric("Current Ratio", "—" if pd.isna(latest["current_ratio"]) else f"{latest['current_ratio']:.2f}")

    metric_options = {
        "Tobin's Q": "tobins_q",
        "ROA": "roa",
        "Bloomberg ESG Score": "besg_esg_score",
        "Market Capitalization": "market_cap",
        "Current Ratio": "current_ratio",
        "Net Interest Coverage": "net_interest_coverage",
        "Cash from Operations": "cash_from_operations",
        "Cash & Equivalents": "cash_equivalents",
        "Total Assets": "total_assets",
        "Total Liabilities": "total_liabilities",
        "CAPEX": "capex",
        "Net PPE": "net_ppe",
        "Debt to Equity": "total_debt_to_equity",
    }
    metric_label = st.selectbox("Metric timeline", list(metric_options))
    metric = metric_options[metric_label]
    plot = company_fin.dropna(subset=[metric]).sort_values("fiscal_year")

    if plot.empty:
        st.info(f"No values are available for {metric_label} in the selected year range.")
    else:
        fig = px.line(
            plot,
            x="fiscal_year",
            y=metric,
            markers=True,
            title=f"{selected_company}: {metric_label}",
            labels={"fiscal_year": "Fiscal year", metric: metric_label},
        )
        fig.update_layout(height=450, margin=dict(l=10, r=10, t=55, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Financial-history table")
    display_cols = [
        "fiscal_year", "tobins_q", "roa", "besg_esg_score", "market_cap",
        "current_ratio", "net_interest_coverage", "total_debt_to_equity",
        "cash_from_operations", "cash_equivalents", "total_assets",
        "total_liabilities", "capex", "net_ppe"
    ]
    st.dataframe(company_fin[display_cols].sort_values("fiscal_year", ascending=False), use_container_width=True, hide_index=True)

    st.download_button(
        "Download selected company history (CSV)",
        data=company_fin.to_csv(index=False).encode("utf-8"),
        file_name=f"{selected_company.replace(' ', '_')}_financial_history.csv",
        mime="text/csv",
    )

footer()
