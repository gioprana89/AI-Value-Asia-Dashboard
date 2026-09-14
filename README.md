# Bloomberg AI & Financial Value in Asia — Dashboard V1

**Designed and developed by Abdillah Arif Nasution, Aulia Arif Nasution & Prana Ugiana Gio**

## What is included
- Executive Overview
- AI Landscape
- Company Explorer
- Data Quality
- About / authorship
- Bloomberg workbook preprocessing script
- Processed CSV tables generated from the current workbook:
  - `company_master.csv`
  - `ai_company.csv`
  - `financial_panel.csv`

## Current data snapshot
- Company universe: 22,825
- Asian Artificial Intelligence-theme companies: 33
- Countries represented in AI sample: 6
- Financial-panel companies: 74
- Financial firm-year observations: 654
- AI–financial overlapping companies: 0

Because current AI–financial overlap is 0, V1 intentionally does **not** activate causal/relationship pages.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Refresh when a new Bloomberg workbook arrives
Put the new workbook somewhere accessible and run:
```bash
python prepare_data.py --input "Bloomberg AI Data.xlsx" --output data/processed
streamlit run app.py
```

## Measurement note
Bloomberg raw AI Revenue Assessment / Theme Assessment uses lower values for stronger exposure.
Dashboard transforms:
- AI Revenue Strength = 4 − Revenue Assessment
- AI Theme Strength = 4 − Theme Assessment
- Composite AI Strength = average of the two

Raw Bloomberg assessment values are retained in the processed AI table.

## Next version
Once Bloomberg annual financial history is collected for the AI-theme companies, V2 can add:
- Financial Resilience Index
- AI → Financial Resilience
- Financial Resilience → Tobin's Q
- ESG moderation
- Conditional indirect effect / moderated mediation
- Company Explorer
