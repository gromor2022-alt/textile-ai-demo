import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
from openai import OpenAI

# =============================
# PASSWORD PROTECTION
# =============================

PASSWORD = "affinexa123"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:

    st.title("🔒 Textile AI Demo Access")

    password = st.text_input("Enter Demo Password", type="password")

    if password == PASSWORD:
        st.session_state.authenticated = True
        st.rerun()
    else:
        st.stop()

# =============================
# PAGE SETUP
# =============================

st.set_page_config(page_title="Textile AI Dashboard", layout="wide")

st.title("🧵 Textile Wholesaler AI Dashboard")

st.caption("Enterprise intelligence dashboard for textile wholesalers")

# =============================
# OPENROUTER CLIENT
# =============================

client = OpenAI(
    api_key=st.secrets["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

# =============================
# DEMO DATA GENERATOR
# =============================

def generate_demo_data():

    customers = [
        "Shree Fabrics","Global Textiles","ABC Exports",
        "Royal Sarees","Delhi Cloth House","Om Traders",
        "Vikas Garments","Shiv Textiles"
    ]

    products = [
        "Rayon Print","Cotton Lawn","Silk Saree",
        "Banarasi Saree","Denim Fabric",
        "Chiffon Saree","Dress Material"
    ]

    categories = [
        "Fabric","Fabric","Saree","Saree",
        "Fabric","Saree","Dress Material"
    ]

    rows = []

    start = datetime.now() - timedelta(days=180)

    for i in range(700):

        date = start + timedelta(days=np.random.randint(0,180))

        cust = np.random.choice(customers)

        p = np.random.randint(0,len(products))

        product = products[p]
        category = categories[p]

        qty = np.random.randint(20,150)

        price = np.random.randint(200,800)

        cost = price * 0.65

        revenue = qty * price

        rows.append([
            date,cust,product,category,
            qty,price,cost,revenue
        ])

    df = pd.DataFrame(rows,columns=[
        "Date","Customer","Product","Category",
        "Quantity","Price","Cost","Amount"
    ])

    return df

# =============================
# DATA LOADING
# =============================

uploaded = st.file_uploader("Upload Dataman Excel Export",type=["xlsx","csv"])

if uploaded:

    if uploaded.name.endswith(".csv"):
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_excel(uploaded)

else:

    if st.button("Load Demo Data"):

        df = generate_demo_data()

        st.session_state["data"] = df

    if "data" in st.session_state:

        df = st.session_state["data"]

    else:
        st.stop()

df["Date"] = pd.to_datetime(df["Date"])

# =============================
# CEO DASHBOARD (Enterprise look)
# =============================

st.subheader("📊 CEO Dashboard")

total_revenue = df["Amount"].sum()
total_customers = df["Customer"].nunique()
total_products = df["Product"].nunique()
total_orders = len(df)

df["Profit"] = df["Amount"] - (df["Quantity"] * df["Cost"])

profit = df["Profit"].sum()

c1,c2,c3,c4,c5 = st.columns(5)

c1.metric("Revenue",f"₹{total_revenue:,.0f}")
c2.metric("Profit",f"₹{profit:,.0f}")
c3.metric("Customers",total_customers)
c4.metric("Products",total_products)
c5.metric("Orders",total_orders)

# =============================
# SALES TREND
# =============================

st.subheader("📈 Sales Trend")

monthly = (
    df.groupby(df["Date"].dt.to_period("M"))["Amount"]
    .sum()
)

monthly.index = monthly.index.astype(str)

fig = px.line(
    monthly.reset_index(),
    x="Date",
    y="Amount",
    markers=True
)

st.plotly_chart(fig,use_container_width=True)

# =============================
# TOP CUSTOMERS
# =============================

st.subheader("🏆 Top Customers")

top_customers = (
    df.groupby("Customer")["Amount"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

fig = px.bar(
    top_customers.reset_index(),
    x="Customer",
    y="Amount"
)

st.plotly_chart(fig,use_container_width=True)

# =============================
# INVENTORY INTELLIGENCE
# =============================

st.subheader("📦 Inventory Intelligence")

top_products = (
    df.groupby("Product")["Quantity"]
    .sum()
    .sort_values(ascending=False)
)

st.dataframe(top_products.head(10))

# =============================
# PROFIT ANALYSIS
# =============================

st.subheader("💰 Profit Margin Analysis")

profit_products = (
    df.groupby("Product")["Profit"]
    .sum()
    .sort_values(ascending=False)
)

fig = px.bar(
    profit_products.head(10).reset_index(),
    x="Product",
    y="Profit"
)

st.plotly_chart(fig,use_container_width=True)

# =============================
# CUSTOMER BUYING PATTERNS
# =============================

st.subheader("📉 Customer Buying Patterns")

pattern = (
    df.groupby(["Customer","Category"])["Amount"]
    .sum()
    .reset_index()
)

fig = px.sunburst(
    pattern,
    path=["Customer","Category"],
    values="Amount"
)

st.plotly_chart(fig,use_container_width=True)

# =============================
# SLOW PRODUCTS
# =============================

st.subheader("🐌 Slow Moving Products")

cutoff = df["Date"].max() - pd.Timedelta(days=90)

recent_products = df[df["Date"] > cutoff]["Product"].unique()

slow_products = df[~df["Product"].isin(recent_products)]["Product"].unique()

if len(slow_products)==0:

    st.success("No slow products detected")

else:

    st.write(list(slow_products))

# =============================
# REORDER ALERTS
# =============================

st.subheader("🔔 Reorder Alerts")

avg_sales = (
    df.groupby("Product")["Quantity"]
    .mean()
)

alerts = avg_sales.sort_values(ascending=False).head(5)

st.dataframe(alerts)

# =============================
# AI INSIGHTS PANEL
# =============================

st.subheader("🤖 AI Business Insights")

summary = df.head(200).to_csv(index=False)

prompt = f"""
You are a textile business analyst.

Here is sales data:

{summary}

Provide 5 key business insights.
"""

response = client.chat.completions.create(
    model="openrouter/auto",
    messages=[{"role":"user","content":prompt}]
)

st.write(response.choices[0].message.content)

# =============================
# AI BUSINESS ASSISTANT
# =============================

st.subheader("💬 Ask AI About Your Business")

question = st.text_input("Example: Which customers contribute most revenue?")

if question:

    prompt = f"""
You are a textile business consultant.

Data sample:

{summary}

Answer this question:

{question}
"""

    response = client.chat.completions.create(
        model="openrouter/auto",
        messages=[{"role":"user","content":prompt}]
    )

    st.write(response.choices[0].message.content)