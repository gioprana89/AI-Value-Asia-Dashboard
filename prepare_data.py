
from pathlib import Path
import argparse
import re
import pandas as pd
import numpy as np

COUNTRY_MAP = {
    "CH":"China","IN":"India","JP":"Japan","KS":"South Korea","HK":"Hong Kong",
    "TT":"Taiwan","IJ":"Indonesia","MK":"Malaysia","TB":"Thailand","SP":"Singapore",
}
TARGET_CODES = set(COUNTRY_MAP)

def normalize_numeric_ticker(value):
    if pd.isna(value):
        return None
    s = str(value).strip()
    if re.fullmatch(r"\d+(\.0+)?", s):
        return str(int(float(s)))
    return s

def normalize_ai_security_key(ticker):
    s = str(ticker).replace(" Equity","").strip()
    parts = s.split()
    if len(parts) >= 2:
        tk, cc = parts[0], parts[1]
        if tk.isdigit():
            tk = str(int(tk))
        return f"{tk} {cc}"
    return s

def build(input_file, output_dir):
    input_file = Path(input_file)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    raw = pd.read_excel(input_file, sheet_name="ALL", header=None)
    company = raw.iloc[1:,:5].copy()
    company.columns=["ticker","country_code","company","esg_disclosure_score","ipo_date"]
    company["ticker"]=company["ticker"].map(normalize_numeric_ticker)
    company["country_code"]=company["country_code"].astype(str).str.strip()
    company["country_name"]=company["country_code"].map(COUNTRY_MAP)
    company["company"]=company["company"].astype(str).str.strip()
    company["esg_disclosure_score"]=pd.to_numeric(company["esg_disclosure_score"],errors="coerce")
    company["ipo_date"]=pd.to_datetime(company["ipo_date"],errors="coerce")
    company["security_key"]=company["ticker"].astype(str)+" "+company["country_code"]
    company=company[company["country_code"].isin(TARGET_CODES)].reset_index(drop=True)

    ai=pd.read_excel(input_file,sheet_name="AI Capability")
    ai.columns=[str(c).strip() for c in ai.columns]
    ai=ai[ai["BI Theme Universe"].astype(str).str.strip().eq("Artificial Intelligence")].copy()
    ai=ai[ai["Country"].isin(TARGET_CODES)].copy()
    ai["security_key"]=ai["Ticker"].map(normalize_ai_security_key)
    ai["revenue_assessment"]=pd.to_numeric(ai["BI Rev. Assessment"],errors="coerce")
    ai["theme_assessment"]=pd.to_numeric(ai["BI Theme Assessment"],errors="coerce")
    ai["total_assessment"]=pd.to_numeric(ai["Total Assessment Sum"],errors="coerce")
    ai["ai_revenue_strength"]=4-ai["revenue_assessment"]
    ai["ai_theme_strength"]=4-ai["theme_assessment"]
    ai["ai_composite_strength"]=(ai["ai_revenue_strength"]+ai["ai_theme_strength"])/2
    ai=ai.merge(company[["security_key","esg_disclosure_score","ipo_date"]].drop_duplicates("security_key"),on="security_key",how="left")
    ai=ai.rename(columns={
        "Ticker":"bloomberg_ticker","Country":"country_code","Country Name":"country_name",
        "Company":"company","BI Exposure Category":"exposure_category","Region":"region",
        "Industry":"industry","MktCap Grp":"market_cap_group"
    })
    ai=ai[[
        "security_key","bloomberg_ticker","country_code","country_name","company",
        "exposure_category","region","industry","market_cap_group",
        "revenue_assessment","theme_assessment","total_assessment",
        "ai_revenue_strength","ai_theme_strength","ai_composite_strength",
        "esg_disclosure_score","ipo_date"
    ]]

    fraw=pd.read_excel(input_file,sheet_name="Filter",header=None)
    metrics={9:"cash_from_operations",10:"total_assets",11:"net_interest_coverage",12:"current_ratio",
             13:"total_debt_to_equity",14:"besg_esg_score",15:"market_cap",16:"total_liabilities",
             17:"tobins_q",18:"roa",20:"capex",21:"net_ppe",22:"esg_disclosure_score",23:"cash_equivalents"}
    rec=[]; ct=cc=cn=None
    for _,row in fraw.iterrows():
        if pd.notna(row[5]) and pd.notna(row[6]) and pd.notna(row[7]):
            ct=normalize_numeric_ticker(row[5]); cc=str(row[6]).strip(); cn=str(row[7]).strip()
        d=row[8]
        if isinstance(d,str) and d.startswith("FY "):
            y=pd.to_numeric(d.replace("FY ",""),errors="coerce")
            if pd.isna(y) or ct is None: continue
            r={"ticker":ct,"country_code":cc,"country_name":COUNTRY_MAP.get(cc,cc),"company":cn,"fiscal_year":int(y)}
            for idx,name in metrics.items():
                r[name]=pd.to_numeric(row[idx],errors="coerce")
            r["security_key"]=f"{ct} {cc}"
            rec.append(r)
    fin=pd.DataFrame(rec).sort_values(["security_key","fiscal_year"]).reset_index(drop=True)

    company.to_csv(output_dir/"company_master.csv",index=False)
    ai.to_csv(output_dir/"ai_company.csv",index=False)
    fin.to_csv(output_dir/"financial_panel.csv",index=False)
    print(f"Saved {len(company):,} company rows, {len(ai):,} AI companies, {len(fin):,} financial firm-years.")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True,help="Path to Bloomberg AI Data.xlsx")
    p.add_argument("--output",default="data/processed",help="Output directory")
    args=p.parse_args()
    build(args.input,args.output)
