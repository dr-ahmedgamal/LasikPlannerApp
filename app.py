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

st.markdown(
    "<h2 style='text-align: center; color: #2c6e91;'>Refractive Surgery Planning Tool</h2>",
    unsafe_allow_html=True,
)

st.markdown("---")

st.markdown("### 👁️ Enter Patient Data")

col1, col2, col3, col4 = st.columns(4)

with col1:
    age = st.number_input("Age", value=18)
with col2:
    sphere = st.number_input("Sphere (D)", step=0.25, value=0.00, format="%.2f")
with col3:
    cylinder = st.number_input("Cylinder (D)", step=0.25, value=0.00, format="%.2f")
with col4:
    bcva_pre = st.number_input("BCVA", value=1.0, format="%.2f")

col5, col6, col7, col8 = st.columns(4)

with col5:
    k1_pre = st.number_input("K1 (D)", step=0.1, value=43.0, format="%.2f")
with col6:
    k2_pre = st.number_input("K2 (D)", step=0.1, value=44.0, format="%.2f")
with col7:
    pachy_pre = st.number_input("Pachymetry (µm)", value=520)
with col8:
    optical_zone = st.number_input("Optical Zone (mm)", step=0.1, value=6.5, format="%.2f")

# Spacer
st.markdown("")

# Upload section
st.markdown("##### Upload Patient Data (optional)")
uploaded_file = st.file_uploader("Choose a CSV or TXT file", type=["csv", "txt"])

# Load uploaded file if provided
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        if not df.empty:
            row = df.iloc[0]
            age = row.get("Age", age)
            sphere = row.get("Sphere", sphere)
            cylinder = row.get("Cylinder", cylinder)
            bcva_pre = row.get("BCVA", bcva_pre)
            k1_pre = row.get("K1", k1_pre)
            k2_pre = row.get("K2", k2_pre)
            pachy_pre = row.get("Pachymetry", pachy_pre)
            optical_zone = row.get("OpticalZone", optical_zone)
            st.success("Data loaded from uploaded file.")
    except Exception as e:
        st.error(f"Error loading file: {e}")

# Spacer
st.markdown("")

# Enlarge and style the button
button_style = """
    <style>
    div.stButton > button:first-child {
        background-color: #2c6e91;
        color: white;
        font-size: 22px;
        font-weight: bold;
        padding: 0.8em 2.5em;
        border-radius: 10px;
    }
    </style>
"""
st.markdown(button_style, unsafe_allow_html=True)

if st.button("Refractive Plan"):
    k1_post, k2_post = calculate_postop_k(k1_pre, k2_pre, sphere, cylinder)
    k_avg_pre = (k1_pre + k2_pre) / 2
    k_avg_post = (k1_post + k2_post) / 2

    pachy_post, ablation_depth = calculate_postop_pachymetry(pachy_pre, sphere, cylinder, optical_zone)
    bcva_post = calculate_postop_bcva(bcva_pre, sphere)
    recommendation = determine_surgery(sphere, cylinder, pachy_pre, pachy_post, k_avg_post, age)
    warnings = check_warnings(k_avg_pre, pachy_pre, pachy_post, sphere, bcva_post, cylinder)

    st.markdown("### 🔍 Results")
    st.write(f"**Post-op K1:** {k1_post} D")
    st.write(f"**Post-op K2:** {k2_post} D")
    st.write(f"**Post-op K Average:** {round(k_avg_post, 2)} D")
    st.write(f"**Post-op Pachymetry:** {pachy_post} µm")
    st.write(f"**Ablation Depth:** {ablation_depth} µm")
    st.write(f"**Post-op BCVA:** {bcva_post}")
    st.markdown("### ✅ Recommended Procedure")
    st.success(recommendation)

    if warnings:
        st.markdown("### ⚠️ Warnings")
        for warn in warnings:
            st.warning(warn)
