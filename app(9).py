import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------------- CONFIG
st.set_page_config(page_title="Retail Arcade", page_icon="🛍️", layout="wide")

CAT_COLOR = {"Beauty": "#C28336", "Clothing": "#00A9B4", "Electronics": "#007E61"}
GOOD, BAD, ACCENT, GOLD = "#3FB950", "#F0616D", "#14B8A6", "#E8A33D"

st.markdown("""
<style>
:root{color-scheme:dark}
.stApp{background:#0B1220;}
[data-testid="stMetric"]{background:#131C2E;border:1px solid #1F2C42;border-radius:14px;padding:14px 16px;}
[data-testid="stMetricLabel"]{color:#8A97AB;}
[data-testid="stSidebar"]{background:#0F1626;}
h1,h2,h3{color:#E5E7EB;}
.insight-box{background:#131C2E;border:1px solid #1F2C42;border-radius:12px;padding:16px 18px;margin-top:8px;}
.insight-box b{color:#E8A33D;}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------- DATA
@st.cache_data
def load_data():
    df = pd.read_csv("retail_sales_data.csv", parse_dates=["Date"])
    df["Month"] = df["Date"].dt.strftime("%b")
    df["Month#"] = df["Date"].dt.month
    df["Quarter"] = "Q" + df["Date"].dt.quarter.astype(str)
    df["Weekday"] = df["Date"].dt.day_name().str[:3]
    bins = [0, 25, 35, 45, 55, 65]
    labels = ["18-25", "26-35", "36-45", "46-55", "56-65"]
    df["Age Band"] = pd.cut(df["Age"], bins=bins, labels=labels, include_lowest=True)
    df["Price Tier"] = df["Price per Unit"].apply(lambda p: "Budget (≤₹50)" if p <= 50 else "Premium (≥₹300)")
    return df


df = load_data()

# ---------------------------------------------------------------- HEADER
st.title("🛍️ Retail Arcade")
st.caption(f"{len(df):,} transactions · 2023 · Every number below is computed live from the filtered rows")

# ---------------------------------------------------------------- SIDEBAR FILTERS
st.sidebar.header("Filters")
cats = st.sidebar.multiselect("Category", sorted(df["Product Category"].unique()),
                               default=sorted(df["Product Category"].unique()))
gender = st.sidebar.radio("Gender", ["All", "Female", "Male"], horizontal=True)
bands = st.sidebar.multiselect("Age Band", ["18-25", "26-35", "36-45", "46-55", "56-65"],
                                default=["18-25", "26-35", "36-45", "46-55", "56-65"])
quarters = st.sidebar.multiselect("Quarter", ["Q1", "Q2", "Q3", "Q4"], default=["Q1", "Q2", "Q3", "Q4"])
tiers = st.sidebar.multiselect("Price Tier", df["Price Tier"].unique().tolist(),
                                default=df["Price Tier"].unique().tolist())

f = df[
    df["Product Category"].isin(cats)
    & df["Age Band"].isin(bands)
    & df["Quarter"].isin(quarters)
    & df["Price Tier"].isin(tiers)
]
if gender != "All":
    f = f[f["Gender"] == gender]

if st.sidebar.button("Reset filters"):
    st.rerun()

st.sidebar.markdown(f"**Showing {len(f):,} of {len(df):,} transactions**")

if f.empty:
    st.warning("No transactions match those filters.")
    st.stop()

# ---------------------------------------------------------------- KPIs
c1, c2, c3, c4 = st.columns(4)
c1.metric("Revenue", f"₹{f['Total Amount'].sum():,.0f}")
c2.metric("Transactions", f"{len(f):,}")
c3.metric("Units Sold", f"{f['Quantity'].sum():,}")
c4.metric("Unique Customers", f"{f['Customer ID'].nunique():,}")

st.divider()

# ---------------------------------------------------------------- CHARTS ROW 1
col1, col2 = st.columns([1.3, 1])

with col1:
    monthly = (f.groupby(["Month#", "Month"], as_index=False)["Total Amount"].sum()
                 .sort_values("Month#"))
    fig = px.line(monthly, x="Month", y="Total Amount", markers=True,
                  title="Revenue by Month")
    fig.update_traces(line_color=ACCENT, marker_color=ACCENT)
    fig.update_layout(template="plotly_dark", paper_bgcolor="#131C2E", plot_bgcolor="#131C2E",
                       margin=dict(t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    by_cat = f.groupby("Product Category", as_index=False)["Total Amount"].sum()
    fig = px.pie(by_cat, names="Product Category", values="Total Amount", hole=0.55,
                 color="Product Category", color_discrete_map=CAT_COLOR, title="Revenue Share by Category")
    fig.update_layout(template="plotly_dark", paper_bgcolor="#131C2E", margin=dict(t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------- CHARTS ROW 2
col3, col4 = st.columns(2)

with col3:
    by_band = f.groupby("Age Band", as_index=False, observed=True)["Total Amount"].sum()
    fig = px.bar(by_band, x="Age Band", y="Total Amount", title="Revenue by Age Band")
    fig.update_traces(marker_color=GOLD)
    fig.update_layout(template="plotly_dark", paper_bgcolor="#131C2E", plot_bgcolor="#131C2E",
                       margin=dict(t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)

with col4:
    order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    by_wd = f.groupby("Weekday", as_index=False)["Quantity"].sum()
    by_wd["Weekday"] = pd.Categorical(by_wd["Weekday"], categories=order, ordered=True)
    by_wd = by_wd.sort_values("Weekday")
    fig = px.bar(by_wd, x="Weekday", y="Quantity", title="Units Sold by Weekday")
    fig.update_traces(marker_color="#E879F9")
    fig.update_layout(template="plotly_dark", paper_bgcolor="#131C2E", plot_bgcolor="#131C2E",
                       margin=dict(t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------- GENDER x CATEGORY
gxc = f.groupby(["Gender", "Product Category"], as_index=False)["Total Amount"].sum()
fig = px.bar(gxc, x="Product Category", y="Total Amount", color="Gender", barmode="group",
             title="Gender vs Category Spend", color_discrete_map={"Female": "#E879F9", "Male": ACCENT})
fig.update_layout(template="plotly_dark", paper_bgcolor="#131C2E", plot_bgcolor="#131C2E",
                   margin=dict(t=40, b=10))
st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------- INSIGHTS
top_cat = by_cat.sort_values("Total Amount", ascending=False).iloc[0]
top_share = top_cat["Total Amount"] / f["Total Amount"].sum()
budget_share = f[f["Price Tier"].str.startswith("Budget")]["Total Amount"].sum() / f["Total Amount"].sum()

st.markdown(f"""
<div class="insight-box">
<b>Auto-generated insights</b><br>
• <b>{top_cat['Product Category']}</b> leads with {top_share:.1%} of revenue in the current filter.<br>
• Every Customer ID in this dataset is unique — repeat-purchase and retention metrics can't be measured from it.<br>
• Budget-tier items (≤₹50) make up {budget_share:.1%} of revenue shown.<br>
• {f['Customer ID'].nunique():,} customers generated {len(f):,} transactions worth ₹{f['Total Amount'].sum():,.0f}.
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------- TABLE
st.subheader("Transaction Data")
st.dataframe(
    f[["Transaction ID", "Date", "Customer ID", "Gender", "Age", "Product Category",
       "Quantity", "Price per Unit", "Total Amount"]].sort_values("Date"),
    use_container_width=True, hide_index=True
)

csv_bytes = f.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download filtered data as CSV", csv_bytes, "retail_arcade_filtered.csv", "text/csv")
