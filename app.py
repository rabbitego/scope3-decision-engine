import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans

st.set_page_config(page_title="Scope 3 Decision Engine", layout="wide")
st.title("🇮🇳 Scope 3 Decarbonization Decision Engine")

data = {
    "supplier": ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta"],
    "material": ["Palm Oil", "Chemicals", "Palm Oil", "Additives", "Palm Oil", "Chemicals", "Additives", "Palm Oil"],
    "distance_km": [500, 2200, 800, 1200, 3000, 1500, 600, 2500],
    "transport": ["truck", "ship", "truck", "rail", "ship", "truck", "rail", "ship"],
    "quantity_ton": [120, 400, 200, 180, 500, 300, 150, 350],
    "emission_factor": [0.12, 0.05, 0.12, 0.03, 0.05, 0.12, 0.03, 0.05],
    "cost_per_ton": [90000, 70000, 88000, 75000, 69000, 92000, 76000, 71000]
}

df = pd.DataFrame(data)
df["emissions_kg"] = df["distance_km"] * df["quantity_ton"] * df["emission_factor"]

kmeans = KMeans(n_clusters=3, random_state=42)
df["cluster"] = kmeans.fit_predict(df[["emissions_kg"]])

cluster_means = df.groupby("cluster")["emissions_kg"].mean()
high = cluster_means.idxmax()
low = cluster_means.idxmin()

df["risk"] = df["cluster"].map({high: "High", low: "Low"}).fillna("Medium")

carbon_price = st.sidebar.slider("Carbon Price (₹ / ton CO₂)", 1000, 15000, 4000, step=500)
df["carbon_cost"] = df["emissions_kg"] * carbon_price / 1000
df["priority"] = df["emissions_kg"] / df["cost_per_ton"]

st.subheader("Supplier Ranking")
st.dataframe(df.sort_values("priority", ascending=False))

st.subheader("Emissions by Supplier")
st.bar_chart(df.set_index("supplier")["emissions_kg"])
