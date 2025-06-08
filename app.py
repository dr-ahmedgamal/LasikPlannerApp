# app.py

import streamlit as st
import pandas as pd
from logic import (
    calculate_ablation_depth,
    calculate_postop_keratometry,
    calculate_postop_pachymetry,
    calculate_postop_bcva,
    determine_surgery,
    check_warnings,
)

st.title("LASIK Surgical Planner")

st.markdown("### Manual Input Fields")

# Input fields with required defaults and steps
age = st.number_input("Age", min_value=18, max_value=100, value=18, step=1)
k1_pre = st.number_input("Pre-op K1 (D)", value=43.00, step=0.01, format="%.2f")
k2_pre = st.number_input("Pre-op K2 (D)", value=44.00, step=0.01, format="%.2f")
sphere = st.number_input("Sphere (D)", value=0.00, step=0.25, format="%.2f")
cylinder = st.number_input("Cylinder (D)", value=0.00, step=0.25, format="%.2f")
bcva_pre = st.number_input("Pre-op BCVA (LogMAR)", value=0.0, step=0.01, format="%.2f")
pachy_pre = st.number_input("Pre-op Pachymetry (µm)", value=540.0, step=1.0)

optical_zone = st.number_input("Optical Zone (mm)", min_value=5.0, max_value=9.0, value=6.5, step=0.1)

st.markdown('<small>Optional: Upload CSV to Auto-Fill (overrides manual fields)</small>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload patient data CSV", type=["csv"])

# Initialize results placeholders
result_data = {}

if uploaded_file:
    data = pd.read_csv(uploaded_file)
    st.markdown("### Uploaded Data Preview")
    st.dataframe(data)

    # Take first row to fill fields and calculate
    row = data.iloc[0]

    age = int(row.get("Age", age))
    k1_pre = float(row.get("K1_pre", k1_pre))
    k2_pre = float(row.get("K2_pre", k2_pre))
    sphere = float(row.get("Sphere", sphere))
    cylinder = float(row.get("Cylinder", cylinder))
    bcva_pre = float(row.get("BCVA_pre", bcva_pre))
    pachy_pre = float(row.get("Pachymetry_pre", pachy_pre))
    optical_zone = float(row.get("OpticalZone", optical_zone))

if st.button("Calculate"):
    ablation_depth = calculate_ablation_depth(sphere, cylinder, optical_zone)
    k1_post, k2_post, kavg_post = calculate_postop_keratometry(sphere, cylinder, k1_pre, k2_pre)
    pachy_post = calculate_postop_pachymetry(sphere, pachy_pre, ablation_depth)
    bcva_post = calculate_postop_bcva(bcva_pre, sphere)
    surgery = determine_surgery(sphere, cylinder, pachy_pre, pachy_post, kavg_post, age)
    warnings = check_warnings(kavg_post, pachy_pre, pachy_post, cylinder, bcva_post)

    # Show calculated results
    st.subheader("Results:")
    st.write(f"Post-op K1: {k1_post:.2f} D")
    st.write(f"Post-op K2: {k2_post:.2f} D")
    st.write(f"Post-op Average K: {kavg_post:.2f} D")
    st.write(f"Post-op Pachymetry: {pachy_post:.2f} µm")
    st.write(f"Predicted Post-op BCVA (LogMAR): {bcva_post:.2f}")
    st.write(f"Estimated Ablation Depth: {ablation_depth:.2f} µm")

    st.subheader("Surgical Recommendation:")
    st.write(surgery)

    if warnings:
        st.subheader("Warnings:")
        for w in warnings:
            st.warning(w)
