import streamlit as st
import pandas as pd
from logic import (
    calculate_postop_k,
    calculate_ablation_depth,
    calculate_postop_pachymetry,
    calculate_postop_bcva,
    determine_surgery,
    check_warnings
)

st.set_page_config(page_title="Refractive Surgery Planner", layout="centered")

st.title("Refractive Surgery Planner")

st.markdown("### Input Patient Data")

col1, col2, col3, col4 = st.columns(4)

with col1:
    age = st.number_input("Age", min_value=18, max_value=100, value=18, step=1)
with col2:
    sphere = st.number_input("Sphere", value=0.00, step=0.25)
with col3:
    cylinder = st.number_input("Cylinder", value=0.00, step=0.25)
with col4:
    bcva = st.number_input("BCVA", min_value=0.0, max_value=2.0, value=1.0, step=0.1)

col5, col6, col7, col8 = st.columns(4)
with col5:
    k1 = st.number_input("K1", value=43.0, step=0.1)
with col6:
    k2 = st.number_input("K2", value=44.0, step=0.1)
with col7:
    pachy = st.number_input("Pachymetry", min_value=300, max_value=700, value=520, step=1)
with col8:
    optical_zone = st.number_input("Optical Zone (mm)", min_value=5.0, max_value=7.0, value=6.5, step=0.1)

# No divider or upload section here

# CSS to style and center the button with larger size and lighter gray border
st.markdown("""
    <style>
    div.stButton > button:first-child {
        width: 50%;
        height: 3.5em;
        font-size: 1.3em;
        font-weight: bold;
        margin: 0 auto;
        display: block;
        background-color: white;
        color: black;
        border: 2px solid #ccc;  /* lighter gray border */
        border-radius: 10px;
        cursor: pointer;
    }
    div.stButton {
        text-align: center;
        margin-top: 20px;
        margin-bottom: 40px;
    }
    </style>
    """, unsafe_allow_html=True)

if st.button("Refractive Plan"):
    k1_post, k2_post = calculate_postop_k(k1, k2, sphere, cylinder)
    k_avg_pre = (k1 + k2) / 2
    k_avg_post = (k1_post + k2_post) / 2
    pachy_post, ablation_depth = calculate_postop_pachymetry(pachy, sphere, cylinder, optical_zone)
    bcva_post = calculate_postop_bcva(bcva, sphere)

    surgery = determine_surgery(sphere, cylinder, pachy, pachy_post, k_avg_post, ablation_depth, age)
    warnings = check_warnings(k_avg_pre, pachy, pachy_post, sphere, bcva_post, cylinder)

    st.markdown("### 🔬 Results")
    st.write(f"**Post-op K1:** {k1_post} D")
    st.write(f"**Post-op K2:** {k2_post} D")
    st.write(f"**Post-op Kavg:** {round(k_avg_post,2)} D")
    st.write(f"**Ablation Depth:** {ablation_depth} µm")
    st.write(f"**Post-op Pachymetry:** {pachy_post} µm")
    st.write(f"**Post-op BCVA:** {bcva_post}")
    st.markdown(f"### 🏥 Recommended Surgery: **{surgery}**")

    if warnings:
        st.markdown("### ⚠️ Warnings")
        for warning in warnings:
            st.warning(warning)
