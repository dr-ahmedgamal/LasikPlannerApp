import streamlit as st
from logic import (
    calculate_postop_k,
    calculate_ablation_depth,
    calculate_postop_pachymetry,
    calculate_postop_bcva,
    determine_surgery,
    check_warnings,
)

st.title("Refractive Surgery Outcome Predictor")

st.markdown(
    '<p style="font-size:14px; font-weight:600;">Optional: Upload CSV to Auto-Fill (overrides manual fields)</p>',
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file:
    import pandas as pd
    df = pd.read_csv(uploaded_file)
    # Take first row for demo purposes; adjust as needed
    data = df.iloc[0]
    age = int(data.get("age", 25))
    sphere = float(data.get("sphere", 0.0))
    cylinder = float(data.get("cylinder", 0.0))
    bcva = float(data.get("bcva", 1.0))
    k1 = float(data.get("k1", 43.0))
    k2 = float(data.get("k2", 44.0))
    pachymetry = float(data.get("pachymetry", 540.0))
    optical_zone = float(data.get("optical_zone", 6.0))
else:
    # Manual inputs with default zeros for sphere and cylinder
    age = st.number_input("Age", min_value=1, max_value=120, value=25, step=1)
    sphere = st.number_input("Sphere (D)", format="%.2f", value=0.00)
    cylinder = st.number_input("Cylinder (D)", format="%.2f", value=0.00)
    bcva = st.number_input("BCVA (decimal, e.g., 1.0)", format="%.2f", min_value=0.0, max_value=2.0, value=1.0)
    k1 = st.number_input("K1 (D)", format="%.2f", value=43.00)
    k2 = st.number_input("K2 (D)", format="%.2f", value=44.00)
    pachymetry = st.number_input("Pachymetry (µm)", min_value=300.0, max_value=700.0, value=540.0)
    optical_zone = st.number_input("Optical Zone (mm)", min_value=5.0, max_value=7.0, value=6.0, step=0.1)

if st.button("Calculate Outcomes"):

    k1_post, k2_post = calculate_postop_k(k1, k2, sphere, cylinder)
    k_avg_post = round((k1_post + k2_post) / 2, 2)

    pachy_post, ablation_depth = calculate_postop_pachymetry(pachymetry, sphere, cylinder, optical_zone)

    bcva_post = calculate_postop_bcva(bcva, sphere)

    surgery_recommendation = determine_surgery(sphere, cylinder, pachymetry, pachy_post, k_avg_post, age)

    warnings = check_warnings((k1 + k2) / 2, pachymetry, pachy_post, sphere, bcva_post, cylinder)

    st.markdown("### Results")
    st.write(f"Post-op K1: **{k1_post} D**")
    st.write(f"Post-op K2: **{k2_post} D**")
    st.write(f"Post-op Average K: **{k_avg_post} D**")
    st.write(f"Pre-op Pachymetry: **{pachymetry} µm**")
    st.write(f"Post-op Pachymetry: **{pachy_post} µm**")
    st.write(f"Ablation Depth: **{ablation_depth} µm**")
    st.write(f"Pre-op BCVA: **{bcva}**")
    st.write(f"Predicted Post-op BCVA: **{bcva_post}**")

    st.markdown(f"### Recommended Surgery:\n**{surgery_recommendation}**")

    if warnings:
        st.markdown("### Warnings:")
        for w in warnings:
            st.warning(w)
    else:
        st.success("No warnings detected.")

