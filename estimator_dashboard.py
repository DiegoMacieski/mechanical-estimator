import streamlit as st
import pandas as pd
import plotly.express as px

# ✅ set_page_config must be the first Streamlit command
st.set_page_config(page_title="Mechanical Estimation Dashboard", layout="wide")

# 🔧 Company introduction
st.markdown("""
### 🔧 About Tritech Engineering

Tritech Engineering is a specialist mechanical, electrical, and maintenance contractor founded in 1999 and based in Dublin, Ireland. The company delivers complex engineering projects across healthcare, pharmaceutical, industrial, educational, commercial, and residential sectors — providing end-to-end solutions from design and installation to ongoing maintenance.

**🎯 Mission**

Since its foundation, Tritech’s mission has been to deliver complex engineering projects in commercial environments while building long-term partnerships with clients, real estate professionals, and design team members. This mission is supported by the company’s five strategic pillars: People, Partnering, Performance, Prevention, and Process.

**🌟 Core Services**
- Mechanical Engineering: Installation of HVAC systems, industrial piping, and mechanical equipment.
- Electrical Engineering: High-quality MV/LV installations, control systems, instrumentation, and automation.
- Design & Build: Custom solutions focused on energy efficiency and sustainability, especially in HVAC systems.
- Asset Management & PPM: Preventive and corrective maintenance with 24/7 technical support.
- Validation & Reactive Maintenance: Skilled teams available for emergency interventions and technical checks.
""")

# 🚀 App Description
st.title("🔧 Mechanical Estimation Dashboard")
st.markdown("""
This professional estimator app allows you to:
- Upload a Bill of Materials (BOM)
- Filter and analyze costs
- Simulate different project scenarios
- Compare supplier pricing
- Visualize data clearly
""")

# 📂 Data upload and loading
@st.cache_data
def load_data():
    return pd.read_csv("mechanical_estimator_dataset.csv")

df = load_data()

st.sidebar.header("📤 Upload BOM File")
uploaded_file = st.sidebar.file_uploader("Upload Bill of Materials (CSV or Excel)", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

# ✅ Rename columns to English if needed
df.rename(columns={
    "Item": "Item",
    "Categoria": "Category",
    "Quantidade": "Quantity",
    "Unidade": "Unit",
    "Preço Unitário (€)": "Unit Price (€)",
    "Fornecedor": "Supplier",
    "Custo Total (€)": "Total Cost (€)"
}, inplace=True)

# Calculate total cost if missing
if "Total Cost (€)" not in df.columns:
    df["Total Cost (€)"] = df["Quantity"] * df["Unit Price (€)"]

# 🔍 Filters
st.sidebar.header("🔍 Filters")
category = st.sidebar.selectbox("Select Category", options=["All"] + sorted(df['Category'].unique().tolist()))
supplier = st.sidebar.selectbox("Select Supplier", options=["All"] + sorted(df['Supplier'].unique().tolist()))

filtered_df = df.copy()
if category != "All":
    filtered_df = filtered_df[filtered_df['Category'] == category]
if supplier != "All":
    filtered_df = filtered_df[filtered_df['Supplier'] == supplier]

# 📈 Scenario Simulator
st.sidebar.header("🧮 Scenario Simulator")
markup = st.sidebar.slider("Markup (%)", 0, 50, 10)
waste = st.sidebar.slider("Waste Factor (%)", 0, 20, 0)

filtered_df["Adjusted Qty"] = filtered_df["Quantity"] * (1 + waste / 100)
filtered_df["Final Unit Price"] = filtered_df["Unit Price (€)"] * (1 + markup / 100)
filtered_df["Adjusted Cost (€)"] = filtered_df["Adjusted Qty"] * filtered_df["Final Unit Price"]

total_adjusted_cost = filtered_df["Adjusted Cost (€)"].sum()

# 📋 Final Table
st.subheader("📋 Bill of Materials (Filtered and Adjusted)")
st.dataframe(filtered_df, use_container_width=True)

# 💶 Total Estimated Cost
st.subheader("💶 Estimated Total Cost")
st.metric("Adjusted Total Cost", f"€ {total_adjusted_cost:,.2f}")

# 📊 Charts
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Cost by Category")
    fig1 = px.bar(filtered_df.groupby("Category")["Adjusted Cost (€)"].sum().reset_index(),
                  x="Category", y="Adjusted Cost (€)", text_auto=True)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("### 🧱 Cost Distribution (Pie)")
    fig2 = px.pie(filtered_df, names="Category", values="Adjusted Cost (€)", hole=0.3)
    st.plotly_chart(fig2, use_container_width=True)

# ⬇️ Download CSV
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Adjusted BOM (CSV)", data=csv, file_name="adjusted_BOM.csv", mime="text/csv")