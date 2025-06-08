import streamlit as st
import pandas as pd
from logic import (
    calculate_ablation_depth,
    calculate_postop_k,
    calculate_postop_pachymetry,
    calculate_postop_bcva,
    determine_surgery,
    check_warnings,
)

st.title("LASIK Surgical Planner")

# Input fields order and defaults
age = st.number_input("Age", min_value=18, max_value=100, value=18, step=1)

K1_pre = st.number_input("K1 (D)", min_value=36.00, max_value=49.00, value=43.00, step=0.01, format="%.2f")
K2_pre = st.number_input("K2 (D)", min_value=36.00, max_value=49.00, value=44.00, step=0.01, format="%.2f")

sphere = st.number_input("Sphere (D)", value=0.00, step=0.25, format="%.2f")
cylinder = st.number_input("Cylinder (D)", value=0.00, step=0.25, format="%.2f")
pachy_pre = st.number_input("Pre-op Pachymetry (µm)", min_value=350.0, max_value=700.0, value=550.0, step=1.0)

bcva_pre = st.number_input("Pre-op BCVA (decimal)", min_value=0.0, max_value=1.5, value=1.0, step=0.01, format="%.2f")

st.markdown(
    '<small>Optional: Upload CSV to Auto-Fill (overrides manual fields)</small>',
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader("", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.write("### Uploaded Data")
        st.dataframe(df)
        # Auto-fill first row values into input widgets (streamlit can't programmatically set input values,
        # so show data below for reference)
        st.markdown("**Auto-filled from CSV (preview only):**")
        st.write(df.head(1).T)
    except Exception as e:
        st.error(f"Error reading uploaded file: {e}")

if st.button("Calculate Post-op Data"):
    ablation_depth = calculate_ablation_depth(sphere, cylinder)
    K1_post, K2_post = calculate_postop_k(K1_pre, K2_pre, sphere, cylinder)
    k_avg_post = round((K1_post + K2_post) / 2, 2)
    pachy_post = calculate_postop_pachymetry(pachy_pre, ablation_depth)
    bcva_post = calculate_postop_bcva(bcva_pre, sphere)
    surgery = determine_surgery(sphere, cylinder, pachy_pre, pachy_post, k_avg_post, age)
    warnings = check_warnings((K1_pre + K2_pre) / 2, pachy_pre, pachy_post, sphere, bcva_post)

    st.write("### Results")
    st.write(f"**Post-op K1:** {K1_post}")
    st.write(f"**Post-op K2:** {K2_post}")
    st.write(f"**Post-op Avg K:** {k_avg_post}")
    st.write(f"**Post-op Pachymetry:** {pachy_post} µm")
    st.write(f"**Post-op BCVA:** {bcva_post}")
    st.write(f"**Recommended Surgery:** {surgery}")
    st.write(f"**Warnings:** {', '.join(warnings) if warnings else 'None'}")
