# app.py

import streamlit as st
import pandas as pd
from logic import (
    calculate_postop_k,
    calculate_postop_pachymetry,
    calculate_postop_bcva,
    determine_surgery,
    check_warnings
)

st.set_page_config(page_title="LASIK Surgical Planner", layout="centered")
st.title("👁️ LASIK Surgical Planner")

st.subheader("🔢 Manual Input")

with st.form("manual_input_form"):
    age = st.number_input("Age", min_value=18, value=18)
    sphere = st.number_input("Sphere (D)", step=0.25, value=0.00)
    cylinder = st.number_input("Cylinder (D)", step=0.25, value=0.00)
    bcva_pre = st.number_input("Pre-op BCVA", min_value=0.0, max_value=1.5, step=0.1, value=1.0)
    pachy_pre = st.number_input("Pre-op Pachymetry (µm)", min_value=400.0, max_value=700.0, step=1.0, value=520.0)
    K1_pre = st.number_input("Pre-op K1 (D)", min_value=30.0, max_value=60.0, step=0.01, value=43.00)
    K2_pre = st.number_input("Pre-op K2 (D)", min_value=30.0, max_value=60.0, step=0.01, value=44.00)

    submitted = st.form_submit_button("Calculate")

# Display sample upload AFTER manual input
st.markdown("#####")
st.markdown("<small><i>Optional: Upload CSV to Auto-Fill (overrides manual fields)</i></small>", unsafe_allow_html=True)
sample = st.file_uploader("Upload CSV", type=["csv"])

if sample:
    df = pd.read_csv(sample)
    if not df.empty:
        st.success("Sample data loaded. Populating first row.")
        row = df.iloc[0]
        age = int(row['Age'])
        sphere = float(row['Sphere'])
        cylinder = float(row['Cylinder'])
        bcva_pre = float(row['BCVA_pre'])
        pachy_pre = float(row['Pachymetry_pre'])
        K1_pre = float(row['K1_pre'])
        K2_pre = float(row['K2_pre'])
        submitted = True

if submitted:
    K1_post, K2_post = calculate_postop_k(K1_pre, K2_pre, sphere, cylinder)
    k_avg_post = (K1_post + K2_post) / 2
    ablation_depth = (15 if sphere <= 0 else 1) * (abs(sphere) + abs(cylinder))
    pachy_post = calculate_postop_pachymetry(pachy_pre, ablation_depth)
    bcva_post = calculate_postop_bcva(bcva_pre, sphere)
    surgery = determine_surgery(sphere, cylinder, pachy_pre, pachy_post, k_avg_post, age)
    warnings = check_warnings((K1_pre + K2_pre) / 2, pachy_pre, pachy_post, sphere, bcva_post)

    st.subheader("📊 Results")
    st.write(f"**Post-op K1:** {K1_post:.2f} D")
    st.write(f"**Post-op K2:** {K2_post:.2f} D")
    st.write(f"**Post-op Kavg:** {k_avg_post:.2f} D")
    st.write(f"**Post-op Pachymetry:** {pachy_post:.2f} µm")
    st.write(f"**Post-op BCVA:** {bcva_post:.2f}")
    st.write(f"**Recommended Surgery:** {surgery}")
    st.write("**Warnings:** " + (', '.join(warnings) if warnings else "None"))
else:
    st.info("Please enter data manually or upload a CSV to begin.")
