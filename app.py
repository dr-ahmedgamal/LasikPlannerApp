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

st.title("LASIK Surgical Planner")

st.write(
    "<small style='font-size:12px;'>Optional: Upload CSV to Auto-Fill (overrides manual fields)</small>",
    unsafe_allow_html=True,
)

# Manual input fields in specified order with initial values
age = st.number_input("Age", min_value=18, max_value=120, value=18, step=1)
sphere = st.number_input("Sphere", value=0.00, step=0.25, format="%.2f")
cylinder = st.number_input("Cylinder", value=0.00, step=0.25, format="%.2f")
bcva = st.number_input("Pre-op BCVA", min_value=0.0, max_value=1.5, value=1.0, step=0.01, format="%.2f")
k1_pre = st.number_input("K1 (pre-op)", value=43.00, step=0.01, format="%.2f")
k2_pre = st.number_input("K2 (pre-op)", value=44.00, step=0.01, format="%.2f")
pachy_pre = st.number_input("Pachymetry (pre-op)", min_value=300, max_value=700, value=540, step=1)
optical_zone = st.number_input("Optical Zone (mm)", min_value=5.0, max_value=8.0, value=6.0, step=0.1, format="%.1f")

uploaded_file = st.file_uploader("Upload patient data CSV", type=["csv"])

# If CSV uploaded, override manual inputs with first row of CSV data
if uploaded_file is not None:
    df_uploaded = pd.read_csv(uploaded_file)
    if not df_uploaded.empty:
        first_row = df_uploaded.iloc[0]
        age = first_row.get("Age", age)
        sphere = first_row.get("Sphere", sphere)
        cylinder = first_row.get("Cylinder", cylinder)
        bcva = first_row.get("BCVA_pre", bcva)
        k1_pre = first_row.get("K1_pre", k1_pre)
        k2_pre = first_row.get("K2_pre", k2_pre)
        pachy_pre = first_row.get("Pachymetry_pre", pachy_pre)
        optical_zone = first_row.get("Optical_Zone", optical_zone)

if st.button("Calculate Post-op Data and Recommend Surgery"):
    K1_post, K2_post = calculate_postop_k(k1_pre, k2_pre, sphere, cylinder)
    k_avg_post = (K1_post + K2_post) / 2
    ablation_depth = calculate_ablation_depth(sphere, cylinder, optical_zone)
    pachy_post = calculate_postop_pachymetry(pachy_pre, ablation_depth, sphere)
    bcva_post = calculate_postop_bcva(bcva, sphere)
    surgery = determine_surgery(sphere, cylinder, pachy_pre, pachy_post, k_avg_post, age)
    warnings = check_warnings((k1_pre + k2_pre) / 2, pachy_pre, pachy_post, sphere, bcva_post, cylinder)

    st.write("### Results")
    st.write(f"Post-op K1: {K1_post:.2f} D")
    st.write(f"Post-op K2: {K2_post:.2f} D")
    st.write(f"Post-op Average K: {k_avg_post:.2f} D")
    st.write(f"Ablation Depth: {ablation_depth:.2f} µm")
    st.write(f"Post-op Pachymetry: {pachy_post:.2f} µm")
    st.write(f"Post-op BC
