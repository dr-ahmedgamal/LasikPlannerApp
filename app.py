import streamlit as st
import pandas as pd
from logic import (
    calculate_postop_k,
    calculate_postop_pachymetry,
    calculate_postop_bcva,
    determine_surgery,
    check_warnings,
)

st.title("LASIK Surgical Planner")

st.markdown("### Optional: Upload sample CSV to autofill patient data")
uploaded_file = st.file_uploader("Upload CSV file (optional)", type=["csv"])

# Default input values (empty or example)
default_data = {
    "Sphere":  -3.5,
    "Cylinder":  -1.25,
    "BCVA": 0.8,
    "K1_pre": 43.5,
    "K2_pre": 44.0,
    "Pachymetry_pre": 520,
    "Age": 28,
}

input_data = default_data.copy()

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        # Take first row to autofill inputs
        first_row = df.iloc[0]
        input_data = {
            "Sphere": float(first_row.get("Sphere", default_data["Sphere"])),
            "Cylinder": float(first_row.get("Cylinder", default_data["Cylinder"])),
            "BCVA": float(first_row.get("BCVA_pre", default_data["BCVA"])),
            "K1_pre": float(first_row.get("K1_pre", default_data["K1_pre"])),
            "K2_pre": float(first_row.get("K2_pre", default_data["K2_pre"])),
            "Pachymetry_pre": float(first_row.get("Pachymetry_pre", default_data["Pachymetry_pre"])),
            "Age": int(first_row.get("Age", default_data["Age"])),
        }
        st.success("Sample data loaded from CSV to input fields!")
    except Exception as e:
        st.error(f"Error reading uploaded file: {e}")

st.markdown("### Enter Patient Data")

sphere = st.number_input("Sphere (D)", value=input_data["Sphere"], step=0.1, format="%.2f")
cylinder = st.number_input("Cylinder (D)", value=input_data["Cylinder"], step=0.1, format="%.2f")
bcva_pre = st.number_input("Pre-op BCVA (decimal, e.g., 0.8)", value=input_data["BCVA"], min_value=0.0, max_value=2.0, step=0.01, format="%.2f")
k1_pre = st.number_input("Pre-op K1 (D)", value=input_data["K1_pre"], step=0.1, format="%.2f")
k2_pre = st.number_input("Pre-op K2 (D)", value=input_data["K2_pre"], step=0.1, format="%.2f")
pachy_pre = st.number_input("Pre-op Pachymetry (µm)", value=input_data["Pachymetry_pre"], step=1)
age = st.number_input("Age (years)", value=input_data["Age"], min_value=10, max_value=100, step=1)

if st.button("🔍 Calculate Results"):
    # Calculations
    K1_post, K2_post = calculate_postop_k(k1_pre, k2_pre, sphere, cylinder)
    k_avg_post = (K1_post + K2_post) / 2

    if sphere <= 0:
        ablation_depth = 15 * (abs(sphere) + abs(cylinder))
    else:
        ablation_depth = 1 * (abs(sphere) + abs(cylinder))

    pachy_post = calculate_postop_pachymetry(pachy_pre, ablation_depth)
    bcva_post = calculate_postop_bcva(bcva_pre, sphere)
    surgery = determine_surgery(sphere, cylinder, pachy_pre, pachy_post, k_avg_post, age)
    warnings = check_warnings(k_avg_post, pachy_pre, pachy_post, sphere, bcva_post)

    st.markdown("### Results")
    st.write(f"**Post-op K1:** {K1_post:.2f} D")
    st.write(f"**Post-op K2:** {K2_post:.2f} D")
    st.write(f"**Post-op Average K:** {k_avg_post:.2f} D")
    st.write(f"**Ablation Depth:** {ablation_depth:.2f} µm")
    st.write(f"**Post-op Pachymetry:** {pachy_post:.2f} µm")
    st.write(f"**Post-op BCVA:** {bcva_post:.2f}")
    st.write(f"**Recommended Surgery:** {surgery}")
    if warnings:
        st.warning("Warnings: " + ", ".join(warnings))
    else:
        st.success("No warnings detected.")

else:
    st.info("Fill the patient data and press 'Calculate Results' to see recommendations.")
