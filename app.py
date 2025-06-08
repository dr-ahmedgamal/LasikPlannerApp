# app.py

import streamlit as st
import pandas as pd
from logic import calculate_postop_k, calculate_postop_pachymetry, calculate_postop_bcva, determine_surgery, check_warnings

st.set_page_config(page_title="LASIK Planner", layout="centered")
st.title('🔍 LASIK Surgical Planner')

st.write("### Step 1: Input Patient Data")

# --- Manual Input First ---
age = st.number_input("Age", min_value=10, max_value=100, value=18, step=1)

col1, col2 = st.columns(2)
with col1:
    sphere = st.number_input("Sphere (D)", value=0.00, format="%.2f", step=0.25)
with col2:
    cylinder = st.number_input("Cylinder (D)", value=0.00, format="%.2f", step=0.25)

col3, col4 = st.columns(2)
with col3:
    K1_pre = st.number_input("Pre-op K1 (D)", value=43.00, format="%.2f")
with col4:
    K2_pre = st.number_input("Pre-op K2 (D)", value=44.00, format="%.2f")

col5, col6 = st.columns(2)
with col5:
    pachy_pre = st.number_input("Pre-op Pachymetry (µm)", value=540, format="%d")
with col6:
    bcva_pre = st.number_input("Pre-op BCVA", value=0.8, format="%.2f")

# --- Optional Upload AFTER Manual Inputs ---
st.write("### Optional: Upload CSV to Auto-Fill (overrides manual fields)")
uploaded_file = st.file_uploader("Upload sample data CSV", type=["csv"])

# --- Auto-fill if CSV uploaded ---
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    patient = df.iloc[0]
    sphere = patient['Sphere']
    cylinder = patient['Cylinder']
    K1_pre = patient['K1_pre']
    K2_pre = patient['K2_pre']
    pachy_pre = patient['Pachymetry_pre']
    bcva_pre = patient['BCVA_pre']
    age = patient['Age']

# --- Submit ---
if st.button("📊 Calculate Results"):
    K1_post, K2_post = calculate_postop_k(K1_pre, K2_pre, sphere, cylinder)
    k_avg_post = (K1_post + K2_post) / 2
    ablation_depth = 15 * (abs(sphere) + abs(cylinder)) if sphere <= 0 else 1 * (abs(sphere) + abs(cylinder))
    pachy_post = calculate_postop_pachymetry(pachy_pre, ablation_depth)
    bcva_post = calculate_postop_bcva(bcva_pre, sphere)
    surgery = determine_surgery(sphere, cylinder, pachy_pre, pachy_post, k_avg_post, age)
    warnings = check_warnings((K1_pre + K2_pre) / 2, pachy_pre, pachy_post, sphere, bcva_post)

    st.write("### ✅ Results")
    st.write(f"**Post-op K1:** {K1_post:.2f} D")
    st.write(f"**Post-op K2:** {K2_post:.2f} D")
    st.write(f"**Post-op Kavg:** {k_avg_post:.2f} D")
    st.write(f"**Post-op Pachymetry:** {pachy_post:.2f} µm")
    st.write(f"**Post-op BCVA:** {bcva_post:.2f}")
    st.write(f"**Recommended Surgery:** {surgery}")
    
    if warnings:
        st.warning(" ⚠ Warnings: " + " | ".join(warnings))
    else:
        st.success("✅ No warnings detected.")
