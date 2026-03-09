import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
import urllib.parse
from openai import OpenAI

# =============================
# PASSWORD
# =============================

PASSWORD = "affinexa123"

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:

    st.title("🔒 Textile AI Demo")

    p = st.text_input("Enter password", type="password")

    if p == PASSWORD:
        st.session_state.auth = True
        st.rerun()
    else:
        st.stop()

# =============================
# PAGE
# =============================

st.set_page_config(page_title="Textile AI", layout="wide")

st.title("🧵 Textile Wholesaler AI Dashboard")

# =============================
# AI CLIENT
# =============================

client = OpenAI(
    api_key=st.secrets["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

# =============================
# DEMO DATA
# =============================

def demo_data():

    customers = [
        "Shree Fabrics","Global Textiles","Royal Sarees",
        "Delhi Cloth House","Om Traders","ABC Exports"
    ]

    products = [
        "Rayon Print","Cotton Lawn","Silk Saree",
        "Banarasi Saree","Denim Fabric","Chiffon Saree"
    ]

    rows = []

    start = datetime.now() - timedelta(days=180)

    for i in range(600):

        date = start + timedelta(days=np.random.randint(0,180))
        cust = np.random.choice(customers)
        prod = np.random.choice(products)

        qty = np.random.randint(10,120)
        price = np.random.randint(200,700)
        cost = price * 0.65

        rows.append([
            date,cust,prod,
            qty,price,cost,
            qty*price
        ])

    df = pd.DataFrame(rows,columns=[
        "Date","Customer","Product",
        "Quantity","Price","Cost","Amount"
    ])

    return df

if "data" not in st.session_state:
    st.session_state.data = demo_data()

df = st.session_state.data

df["Profit"] = df["Amount"] - df["Quantity"]*df["Cost"]

# =============================
# CEO DASHBOARD
# =============================

st.subheader("📊 CEO Dashboard")

c1,c2,c3,c4,c5 = st.columns(5)

c1.metric("Revenue",f"₹{df['Amount'].sum():,.0f}")
c2.metric("Profit",f"₹{df['Profit'].sum():,.0f}")
c3.metric("Customers",df["Customer"].nunique())
c4.metric("Products",df["Product"].nunique())
c5.metric("Orders",len(df))

# =============================
# SALES TREND
# =============================

st.subheader("📈 Sales Trend")

monthly = df.groupby(df["Date"].dt.to_period("M"))["Amount"].sum()

monthly.index = monthly.index.astype(str)

fig = px.line(monthly.reset_index(),x="Date",y="Amount")

st.plotly_chart(fig,use_container_width=True)

# =============================
# TOP CUSTOMERS
# =============================

st.subheader("🏆 Top Customers")

top = df.groupby("Customer")["Amount"].sum().sort_values(ascending=False).head(10)

st.bar_chart(top)

# =============================
# INVENTORY INTELLIGENCE
# =============================

st.subheader("📦 Inventory Intelligence")

inv = df.groupby("Product")["Quantity"].sum().sort_values(ascending=False)

st.dataframe(inv)

# =============================
# PROFIT ANALYSIS
# =============================

st.subheader("💰 Profit Analysis")

profit = df.groupby("Product")["Profit"].sum()

st.bar_chart(profit)

# =============================
# CUSTOMER BUYING PATTERNS
# =============================

st.subheader("📉 Customer Buying Pattern")

pattern = df.groupby(["Customer","Product"])["Amount"].sum().reset_index()

fig = px.sunburst(pattern,path=["Customer","Product"],values="Amount")

st.plotly_chart(fig,use_container_width=True)

# =============================
# SLOW PRODUCTS
# =============================

st.subheader("🐌 Slow Products")

cutoff = datetime.now()-timedelta(days=90)

recent = df[df["Date"]>cutoff]["Product"].unique()

slow = df[~df["Product"].isin(recent)]["Product"].unique()

st.write(list(slow))

# =============================
# REORDER ALERT
# =============================

st.subheader("🔔 Reorder Alerts")

avg = df.groupby("Product")["Quantity"].mean().sort_values(ascending=False).head()

st.dataframe(avg)

# =============================
# SALES FORECAST
# =============================

st.subheader("🔮 6 Month Sales Forecast")

future = []

base = monthly.iloc[-1]

for i in range(6):
    base *= 1.05
    future.append(base)

forecast = pd.DataFrame({
    "Month":range(1,7),
    "Forecast":future
})

st.line_chart(forecast)

# =============================
# CUSTOMER RISK
# =============================

st.subheader("⚠ Customer Risk Detection")

last_buy = df.groupby("Customer")["Date"].max()

risk = last_buy[last_buy < datetime.now()-timedelta(days=60)]

st.write(risk)

# =============================
# BUSINESS REPORT
# =============================

st.subheader("📑 Generate Business Report")

if st.button("Create Report"):

    file = "report.pdf"

    c = canvas.Canvas(file)

    c.drawString(100,800,"Textile Business Report")

    c.drawString(100,760,f"Revenue {df['Amount'].sum():,.0f}")

    c.drawString(100,730,f"Profit {df['Profit'].sum():,.0f}")

    c.save()

    with open(file,"rb") as f:
        st.download_button("Download PDF",f,"report.pdf")

# =============================
# AI INSIGHTS
# =============================

st.subheader("🤖 AI Insights")

sample = df.head(200).to_csv(index=False)

prompt = f"""
You are a textile business analyst.

Data:
{sample}

Give 5 insights.
"""

r = client.chat.completions.create(
    model="openrouter/auto",
    messages=[{"role":"user","content":prompt}]
)

st.write(r.choices[0].message.content)

# =============================
# NATURAL LANGUAGE DASHBOARD
# =============================

st.subheader("💬 Ask AI")

q = st.text_input("Ask about your business")

if q:

    prompt = f"""
Data:
{sample}

Question:
{q}
"""

    r = client.chat.completions.create(
        model="openrouter/auto",
        messages=[{"role":"user","content":prompt}]
    )

    st.write(r.choices[0].message.content)

# =============================
# WHATSAPP ALERT
# =============================

st.subheader("📱 WhatsApp Alert")

msg = f"Sales today ₹{df['Amount'].sum():,.0f}"

encoded = urllib.parse.quote(msg)

link = f"https://wa.me/?text={encoded}"

st.link_button("Send WhatsApp Alert",link)