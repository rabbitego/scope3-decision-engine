import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Scope 3 Decision Dashboard",
    layout="wide"
)

st.title("🌍 Scope 3 Emission Decision Dashboard")
st.caption("GChem Procurement | Decision Support System")

# ---------------- DATA ----------------
data = {
    "Supplier": ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta"],
    "Material": ["Palm Oil", "Chemicals", "Palm Oil", "Additives", "Palm Oil", "Chemicals"],
    "Distance_km": [500, 2200, 800, 1200, 3000, 1500],
    "Transport": ["Truck", "Ship", "Truck", "Rail", "Ship", "Truck"],
    "Quantity_ton": [120, 400, 200, 180, 500, 300],
    "Emission_Factor": [0.12, 0.05, 0.12, 0.03, 0.05, 0.12],
    "Cost_per_ton": [90000, 70000, 88000, 75000, 69000, 92000]
}

df = pd.DataFrame(data)

# ---------------- CALCULATIONS ----------------
df["Emissions_kg"] = df["Distance_km"] * df["Quantity_ton"] * df["Emission_Factor"]

kmeans = KMeans(n_clusters=3, random_state=42)
df["Cluster"] = kmeans.fit_predict(df[["Emissions_kg"]])

cluster_mean = df.groupby("Cluster")["Emissions_kg"].mean()
high = cluster_mean.idxmax()
low = cluster_mean.idxmin()

df["Risk_Level"] = df["Cluster"].map({high: "High", low: "Low"}).fillna("Medium")

carbon_price = st.sidebar.slider("💰 Carbon Price (₹ / ton CO₂)", 1000, 15000, 4000, step=500)
df["Carbon_Cost_₹"] = df["Emissions_kg"] * carbon_price / 1000
df["Priority_Score"] = df["Emissions_kg"] / df["Cost_per_ton"]

# ---------------- KPI CARDS ----------------
st.subheader("📌 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Suppliers", len(df))
col2.metric("Total Emissions (kg)", f"{int(df['Emissions_kg'].sum()):,}")
col3.metric("High Risk Suppliers", df[df["Risk_Level"] == "High"].shape[0])
col4.metric("Carbon Cost (₹)", f"{int(df['Carbon_Cost_₹'].sum()):,}")

# ---------------- CHARTS ----------------
st.subheader("📊 Emission & Priority Analysis")

c1, c2 = st.columns(2)

with c1:
    st.markdown("**Emissions by Supplier**")
    st.bar_chart(df.set_index("Supplier")["Emissions_kg"])

with c2:
    st.markdown("**Priority Score (Impact per ₹)**")
    st.bar_chart(df.set_index("Supplier")["Priority_Score"])

# ---------------- TABLE ----------------
st.subheader("📋 Supplier Decision Table")
st.dataframe(
    df[[
        "Supplier",
        "Material",
        "Emissions_kg",
        "Carbon_Cost_₹",
        "Risk_Level",
        "Priority_Score"
    ]].sort_values("Priority_Score", ascending=False),
    use_container_width=True
)

# ---------------- ACTIONS ----------------
st.subheader("🚀 Recommended Actions")

top_suppliers = df.sort_values("Priority_Score", ascending=False).head(3)

for _, row in top_suppliers.iterrows():
    st.success(
        f"Focus on **{row['Supplier']}** → "
        f"High impact supplier with **{int(row['Emissions_kg'])} kg CO₂** "
        f"and strong reduction potential per rupee."
    )
