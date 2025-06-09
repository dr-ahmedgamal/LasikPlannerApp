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

st.markdown("<h1 style='text-align: center; color: #1E90FF;'>🔍 Refractive Surgery Planner</h1>", unsafe_allow_html=True)

# Input form
with st.form(key='patient_data'):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        age = st.number_input("Age", min_value=0, max_value=120, value=18)
    with col2:
        sphere = st.number_input("Sphere (D)", step=0.25, format="%.2f", value=0.00)
    with col3:
        cylinder = st.number_input("Cylinder (D)", step=0.25, format="%.2f", value=0.00)
    with col4:
        bcva_pre = st.number_input("BCVA", min_value=0.0, max_value=2.0, step=0.1, format="%.2f", value=1.0)

    col5, col6, col7, col8 = st.columns(4)
    with col5:
        k1_pre = st.number_input("K1 (D)", step=0.1, format="%.2f", value=42.0)
    with col6:
        k2_pre = st.number_input("K2 (D)", step=0.1, format="%.2f", value=43.0)
    with col7:
        pachymetry = st.number_input("Pachymetry (µm)", step=1, value=520)
    with col8:
        optical_zone = st.number_input("Optical Zone (mm)", step=0.1, format="%.2f", value=6.5)

    # Spacer
    st.markdown("<br>", unsafe_allow_html=True)

    # Upload section
    st.markdown("<p style='font-size: 1rem;'>Upload Patient Data (optional)</p>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["csv", "txt"])

    # Centered large button
    submit = st.form_submit_button(
        label="Refractive Plan"
    )

# Process input
if submit:
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            age = df['Age'][0]
            sphere = df['Sphere'][0]
            cylinder = df['Cylinder'][0]
            bcva_pre = df['BCVA'][0]
            k1_pre = df['K1'][0]
            k2_pre = df['K2'][0]
            pachymetry = df['Pachymetry'][0]
            optical_zone = df['OpticalZone'][0]
        except Exception as e:
            st.error("Error reading uploaded file. Please ensure it has correct headers.")
            st.stop()

    k1_post, k2_post = calculate_postop_k(k1_pre, k2_pre, sphere, cylinder)
    k_avg_pre = (k1_pre + k2_pre) / 2
    k_avg_post = (k1_post + k2_post) / 2
    pachy_post, ablation_depth = calculate_postop_pachymetry(pachymetry, sphere, cylinder, optical_zone)
    bcva_post = calculate_postop_bcva(bcva_pre, sphere)
    surgery = determine_surgery(sphere, cylinder, pachymetry, pachy_post, k_avg_post, age)
    warnings = check_warnings(k_avg_pre, pachymetry, pachy_post, sphere, bcva_post, cylinder)

    st.markdown("---")
    st.subheader("📊 Results")

    st.markdown(f"""
    - **Post-op K1**: {k1_post} D  
    - **Post-op K2**: {k2_post} D  
    - **Post-op Kavg**: {round(k_avg_post, 2)} D  
    - **Post-op BCVA**: {bcva_post}  
    - **Ablation Depth**: {ablation_depth} µm  
    - **Post-op Pachymetry**: {pachy_post} µm  
    """)

    st.markdown(f"### ✅ Recommended Surgery: **{surgery}**")

    if warnings:
        st.markdown("### ⚠️ Warnings")
        for w in warnings:
            st.warning(w)
