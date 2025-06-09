import streamlit as st
from logic import (
    calculate_postop_k,
    calculate_postop_pachymetry,
    calculate_ablation_depth,
    calculate_postop_bcva,
    determine_surgery,
    check_warnings
)

st.set_page_config(page_title="Refractive Surgery Recommendation", layout="centered")

st.title("👁️ AI-Powered Refractive Surgery Planner")

st.markdown("""
This app helps you determine the **most appropriate refractive surgery** for a patient, based on preoperative clinical data.
- Recommendations include: **LASIK**, **PRK**, **Phakic IOL**, and **Pseudophakic IOL**.
- Warning flags alert you to potential risks like ectasia, keratoconus, and extreme refraction.
""")

st.header("📋 Enter Preoperative Data")

col1, col2 = st.columns(2)

with col1:
    sphere = st.number_input("Sphere (D)", value=-4.00, step=0.25)
    cylinder = st.number_input("Cylinder (D)", value=-1.25, step=0.25)
    age = st.number_input("Age (years)", value=28, min_value=10, max_value=90)
    bcva_pre = st.number_input("Pre-op BCVA", value=1.0, min_value=0.0, max_value=2.0, step=0.01)

with col2:
    pachy_pre = st.number_input("Pre-op Pachymetry (µm)", value=530)
    k1_pre = st.number_input("K1 (D)", value=42.5)
    k2_pre = st.number_input("K2 (D)", value=44.0)
    optical_zone = st.number_input("Optical Zone (mm)", value=6.5, step=0.1)

if st.button("🔍 Analyze"):
    # Calculations
    k1_post, k2_post = calculate_postop_k(k1_pre, k2_pre, sphere, cylinder)
    k_avg_pre = (k1_pre + k2_pre) / 2
    k_avg_post = round((k1_post + k2_post) / 2, 2)

    pachy_post, ablation_depth = calculate_postop_pachymetry(pachy_pre, sphere, cylinder, optical_zone)
    bcva_post = calculate_postop_bcva(bcva_pre, sphere)
    recommendation = determine_surgery(sphere, cylinder, pachy_pre, pachy_post, k_avg_post, age, ablation_depth)
    warnings = check_warnings(k_avg_pre, pachy_pre, pachy_post, sphere + (cylinder / 2), bcva_post)

    # Results
    st.subheader("📈 Postoperative Predictions")
    st.markdown(f"""
    - **Ablation Depth**: `{ablation_depth} µm`
    - **Post-op Pachymetry**: `{pachy_post} µm`
    - **Post-op K1 / K2**: `{k1_post} D` / `{k2_post} D`
    - **Post-op K_avg**: `{k_avg_post} D`
    - **Estimated Post-op BCVA**: `{bcva_post}`
    """)

    st.subheader("✅ Surgical Recommendation")
    st.success(f"**Recommended Surgery:** {recommendation}")

    if warnings:
        st.subheader("⚠️ Warnings")
        for w in warnings:
            st.warning(w)
    else:
        st.info("✅ No warning signs detected.")

st.markdown("---")
st.caption("Developed with ❤️ for clinical decision support in refractive surgery.")
