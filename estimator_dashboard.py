import streamlit as st
import pandas as pd
import plotly.express as px

# ✅ set_page_config must be the first Streamlit command
st.set_page_config(page_title="Mechanical Estimation Dashboard", layout="wide")

# 📌 Introduction
st.markdown("""
### 🔧 About Mechanical Estimation

Mechanical estimation is a critical process in construction and engineering projects.  
It involves preparing detailed cost forecasts for equipment, piping, HVAC systems, and other mechanical installations — helping companies make informed decisions before and during execution.  

**🎯 Key Objectives**
- Ensure cost accuracy for project budgeting and planning
- Support procurement and supplier selection
- Identify potential cost savings and risks
- Simulate different project scenarios to improve decision-making

**🌟 Typical Applications**
- Commercial, industrial, and residential projects
- HVAC system design and installation
- Piping and process systems
- Preventive maintenance planning
- Cost benchmarking across suppliers
""")

# 🚀 App Description
st.title("🔧 Mechanical Estimation Dashboard")
st.markdown("""
This professional estimator app allows you to:
- Upload a Bill of Quantities (BOQ)
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

st.sidebar.header("📤 Upload BOQ File")
uploaded_file = st.sidebar.file_uploader("Upload Bill of Quantities (CSV or Excel)", type=["csv", "xlsx"])

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
st.subheader("📋 Bill of Quantities (Filtered and Adjusted)")
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
st.download_button("📥 Download Adjusted BOQ (CSV)", data=csv, file_name="adjusted_BOQ.csv", mime="text/csv")