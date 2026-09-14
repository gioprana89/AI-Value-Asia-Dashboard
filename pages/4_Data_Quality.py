
import streamlit as st
import plotly.express as px
from utils.data_loader import load_all
from utils.styles import apply_style, header, footer

st.set_page_config(page_title="Data Quality | Bloomberg AI Dashboard", page_icon="🧪", layout="wide")
apply_style()
company, ai, fin, quality = load_all()

header(
    "Data Coverage & Quality",
    "Audit the current Bloomberg extract before using it for causal or panel-data analysis."
)

st.dataframe(quality, use_container_width=True, hide_index=True)

overlap = set(ai["security_key"]).intersection(set(fin["security_key"]))
if not overlap:
    st.warning(
        "Current AI-theme firms and the financial-history panel have 0 overlapping companies. "
        "Collect annual Bloomberg financial history for the AI sample before activating AI–financial relationship analysis."
    )

st.subheader("Financial panel coverage by fiscal year")
year = fin.groupby("fiscal_year", as_index=False).agg(
    firm_years=("security_key","size"),
    companies=("security_key","nunique")
)
fig=px.line(
    year, x="fiscal_year", y="companies", markers=True,
    title="Companies with financial observations by fiscal year",
    labels={"fiscal_year":"Fiscal year","companies":"Companies"}
)
fig.update_layout(height=380, margin=dict(l=10,r=10,t=55,b=10))
st.plotly_chart(fig,use_container_width=True)

st.subheader("Missingness in financial fields")
fields=[
    "cash_from_operations","total_assets","net_interest_coverage","current_ratio",
    "total_debt_to_equity","besg_esg_score","market_cap","total_liabilities",
    "tobins_q","roa","capex","net_ppe","esg_disclosure_score","cash_equivalents"
]
miss = []
for col in fields:
    miss.append({
        "field": col,
        "missing_pct": 100*fin[col].isna().mean()
    })
import pandas as pd
miss=pd.DataFrame(miss).sort_values("missing_pct",ascending=False)
fig=px.bar(
    miss, x="missing_pct", y="field", orientation="h",
    title="Financial-panel missingness",
    labels={"missing_pct":"Missing (%)","field":""}
)
fig.update_layout(height=520, margin=dict(l=10,r=10,t=55,b=10))
st.plotly_chart(fig,use_container_width=True)

footer()
