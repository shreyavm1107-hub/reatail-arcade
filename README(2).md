# Retail Arcade 🛍️

An interactive Streamlit dashboard analyzing 1,000 retail transactions from 2023 —
revenue trends, category mix, customer demographics, and spend patterns by gender,
age band, and day of week.

## Features
- Live KPIs: revenue, transactions, units sold, unique customers
- Filters: category, gender, age band, quarter, price tier
- Revenue by month (line), category share (donut), age band (bar), weekday (bar)
- Gender vs category spend comparison
- Auto-generated text insights that update with the filters
- Filtered data table + CSV export

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Data
`retail_sales_data.csv` — 1,000 transactions: Transaction ID, Date, Customer ID,
Gender, Age, Product Category, Quantity, Price per Unit, Total Amount.
