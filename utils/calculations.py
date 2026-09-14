
import pandas as pd

def fmt_pct(x, digits=1):
    if pd.isna(x):
        return "—"
    return f"{x:.{digits}f}%"

def coverage_pct(series):
    if len(series) == 0:
        return 0.0
    return 100.0 * series.notna().mean()

def get_ai_country_counts(ai_df):
    return (
        ai_df.groupby("country_name", as_index=False)
        .size()
        .rename(columns={"size": "ai_companies"})
        .sort_values("ai_companies", ascending=False)
    )

def get_ai_industry_counts(ai_df):
    return (
        ai_df.groupby("industry", as_index=False)
        .size()
        .rename(columns={"size": "ai_companies"})
        .sort_values("ai_companies", ascending=False)
    )
