import streamlit as st
import pandas as pd
from logic import (
    calculate_postop_k,
    calculate_ablation_depth,
    calculate_postop_pachymetry,
    calculate_postop_bcva,
    determine_surgery,
    check_warnings,
)

st.set_page_config(page_title="Refractive Surgery Planner", layout="centered")

st.title("🔍 Refractive Surgery Planner")

st.markdown("### Enter Patient Data")

# Input fields
col1, col2, col3, col4 = st.columns(4)
with col1:
    age = st.number_input("Age", min_value=18, max_value=100, value=18, step=1)
with col2:
    sphere = st.number_input("Sphere", value=0.00, format="%.2f", step=0.25)
with col3:
    cylinder = st.number_input("Cylinder", value=0.00, format="%.2f", step=0.25)
with col4:
    bcva = st.number_input("BCVA", min_value=0.0, max_value=1.5, value=1.0, step=0.1)

col5, col6, col7, col8 = st.columns(4)
with col5:
    k1 = st.number_input("K1", value=43.0, format="%.2f", step=0.1)
with col6:
    k2 = st.number_input("K2", value=44.0, format="%.2f", step=0.1)
with col7:
    pachy = st.number_input("Pachymetry", min_value=300, max_value=700, value=520, step=1)
with col8:
    optical_zone = st.number_input("Optical Zone (mm)", min_value=5.0, max_value=7.0, value=6.5, step=0.1)

# Optional upload
st.markdown("##### Upload Data File (CSV or TXT):", help="Optional. Auto-fill fields from file.")
uploaded_file = st.file_uploader("", type=["csv", "txt"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".txt"):
            df = pd.read_csv(uploaded_file, sep=None, engine="python")

        # Fill inputs with first row
        if not df.empty:
            age = df.at[0, "age"]
            sphere = df.at[0, "sphere"]
            cylinder = df.at[0, "cylinder"]
            bcva = df.at[0, "bcva"]
            k1 = df.at[0, "k1"]
            k2 = df.at[0, "k2"]
            pachy = df.at[0, "pachy"]
            optical_zone = df.at[0, "optical_zone"]
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")

# Button
st.markdown("###")
if st.button("🔎 Analyze and Recommend", help="Run analysis based on input data.", use_container_width=True):
    k1_post, k2_post = calculate_postop_k(k1, k2, sphere, cylinder)
    k_avg_post = round((k1_post + k2_post) / 2, 2)
    k_avg_pre = round((k1 + k2) / 2, 2)

    pachy_post, ablation_depth = calculate_postop_pachymetry(pachy, sphere, cylinder, optical_zone)
    bcva_post = calculate_postop_bcva(bcva, sphere)

    surgery = determine_surgery(sphere, cylinder, pachy, pachy_post, k_avg_post, age)
    warnings = check_warnings(k_avg_pre, pachy, pachy_post, sphere, bcva_post, cylinder)

    st.subheader("📊 Results")
    st.write(f"**Post-op K1:** {k1_post} D")
    st.write(f"**Post-op K2:** {k2_post} D")
    st.write(f"**Post-op Pachymetry:** {pachy_post} µm")
    st.write(f"**Post-op BCVA:** {bcva_post}")
    st.write(f"**Ablation Depth:** {ablation_depth} µm")
    st.write(f"**Recommended Surgery:** {surgery}")

    if warnings:
        st.warning("⚠️ Warnings:")
        for w in warnings:
            st.write(f"- {w}")
