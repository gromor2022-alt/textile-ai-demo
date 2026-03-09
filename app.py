import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
from openai import OpenAI

st.set_page_config(page_title="Textile AI Dashboard", layout="wide")

st.title("🧵 Textile Wholesaler AI Dashboard")

st.write("Upload Dataman sales export or load demo data to analyze business performance.")

# =============================
# OpenRouter Client
# =============================

client = OpenAI(
    api_key=st.secrets["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

# =============================
# Generate Demo Data
# =============================

def generate_demo_data():

    customers = [
        "Shree Fabrics","Global Textiles","ABC Exports",
        "Ravi Traders","Royal Sarees","Kumar Fashion",
        "Delhi Cloth House","Om Traders","Vikas Garments"
    ]

    products = [
        "Rayon Print","Cotton Lawn","Silk Saree",
        "Poly Viscose","Chiffon Saree","Denim Fabric",
        "Banarasi Saree","Dress Material","Linen Fabric"
    ]

    categories = [
        "Fabric","Fabric","Saree","Fabric","Saree",
        "Fabric","Saree","Dress Material","Fabric"
    ]

    rows = []

    start_date = datetime.now() - timedelta(days=180)

    for i in range(800):

        date = start_date + timedelta(days=np.random.randint(0,180))

        cust = np.random.choice(customers)

        p = np.random.randint(0,len(products))

        product = products[p]

        category = categories[p]

        qty = np.random.randint(10,150)

        price = np.random.randint(200,800)

        cost = price * 0.65

        revenue = qty * price

        rows.append([
            date,cust,product,category,qty,price,cost,revenue
        ])

    df = pd.DataFrame(rows,columns=[
        "Date","Customer","Product","Category",
        "Quantity","Price","Cost","Amount"
    ])

    return df


# =============================
# Load Data
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
# SALES SUMMARY
# =============================

st.subheader("📊 Sales Summary")

c1,c2,c3,c4 = st.columns(4)

c1.metric("Total Revenue",f"₹{df['Amount'].sum():,.0f}")

c2.metric("Customers",df["Customer"].nunique())

c3.metric("Products",df["Product"].nunique())

c4.metric("Orders",len(df))


# =============================
# TOP CUSTOMERS
# =============================

st.subheader("🏆 Top Customers")

top_customers = (
    df.groupby("Customer")["Amount"]
    .sum()
    .sort_values(ascending=False)
    .head(50)
)

st.dataframe(top_customers)

fig = px.bar(
    top_customers.reset_index(),
    x="Customer",
    y="Amount",
    title="Top Customer Revenue"
)

st.plotly_chart(fig,use_container_width=True)


# =============================
# LAST 3 MONTH SALES
# =============================

st.subheader("📈 Last 3 Months Sales")

recent = df[df["Date"] > df["Date"].max() - pd.DateOffset(months=3)]

monthly = (
    recent.groupby(recent["Date"].dt.to_period("M"))["Amount"]
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
# SLOW MOVING PRODUCTS
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
# INVENTORY INTELLIGENCE
# =============================

st.subheader("📦 Inventory Intelligence")

product_sales = (
    df.groupby("Product")["Quantity"]
    .sum()
    .sort_values(ascending=False)
)

st.write("Top Selling Products")

st.dataframe(product_sales.head(10))


# =============================
# PROFIT MARGIN ANALYSIS
# =============================

st.subheader("💰 Profit Margin Analysis")

df["Profit"] = df["Amount"] - (df["Quantity"] * df["Cost"])

profit_products = (
    df.groupby("Product")["Profit"]
    .sum()
    .sort_values(ascending=False)
)

fig = px.bar(
    profit_products.head(10).reset_index(),
    x="Product",
    y="Profit",
    title="Top Profit Generating Products"
)

st.plotly_chart(fig,use_container_width=True)


# =============================
# CUSTOMER BUYING PATTERNS
# =============================

st.subheader("📉 Customer Buying Patterns")

customer_patterns = (
    df.groupby(["Customer","Category"])["Amount"]
    .sum()
    .reset_index()
)

fig = px.sunburst(
    customer_patterns,
    path=["Customer","Category"],
    values="Amount"
)

st.plotly_chart(fig,use_container_width=True)


# =============================
# REORDER ALERTS
# =============================

st.subheader("🔔 Reorder Alerts")

avg_sales = (
    df.groupby("Product")["Quantity"]
    .mean()
)

low_stock_products = avg_sales[avg_sales > avg_sales.mean()].head(5)

st.write("Recommended Reorder Products")

st.dataframe(low_stock_products)


# =============================
# DEMAND FORECAST
# =============================

st.subheader("🔮 Demand Forecast")

forecast = (
    df.groupby("Product")["Amount"]
    .mean()
    .sort_values(ascending=False)
    .head(10)
)

fig = px.bar(
    forecast.reset_index(),
    x="Product",
    y="Amount",
    title="Predicted High Demand Products"
)

st.plotly_chart(fig,use_container_width=True)


# =============================
# AI BUSINESS ASSISTANT
# =============================

st.subheader("🤖 Ask AI About Your Business")

question = st.text_input("Example: Who are my top customers?")

if question:

    sample_data = df.head(200).to_csv(index=False)

    prompt = f"""
You are a textile business analyst.

Here is sample sales data:

{sample_data}

Answer the question clearly:

{question}
"""

    response = client.chat.completions.create(
        model="openrouter/auto",
        messages=[{"role":"user","content":prompt}]
    )

    st.write(response.choices[0].message.content)