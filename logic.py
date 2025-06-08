# app.py
import streamlit as st
import pandas as pd
from logic import calculate_postop_k, calculate_postop_pachymetry, calculate_postop_bcva, determine_surgery, check_warnings

st.set_page_config(page_title="LASIK Planner", layout="centered")
st.title('👁️ LASIK Surgical Planner')

st.markdown("### Enter Patient Data")
age = st.number_input("Age", min_value=18, max_value=100, value=18, step=1)
k1_pre = st.number_input("K1 (D)", min_value=30.0, max_value=60.0, value=43.00, step=0.01)
k2_pre = st.number_input("K2 (D)", min_value=30.0, max_value=60.0, value=44.00, step=0.01)
pachy_pre = st.number_input("Pachymetry (µm)", min_value=350.0, max_value=700.0, value=520.0, step=1.0)
bcva_pre = st.number_input("Pre-op BCVA", min_value=0.1, max_value=2.0, value=1.0, step=0.1)
sphere = st.number_input("Sphere (D)", min_value=-20.0, max_value=20.0, value=0.00, step=0.25)
cylinder = st.number_input("Cylinder (D)", min_value=-6.0, max_value=6.0, value=0.00, step=0.25)

st.markdown("<p style='font-size: small;'>Optional: Upload CSV to Auto-Fill (overrides manual fields)</p>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload sample data", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    first_row = df.iloc[0]
    age = first_row['Age']
    k1_pre = first_row['K1_pre']
    k2_pre = first_row['K2_pre']
    pachy_pre = first_row['Pachymetry_pre']
    bcva_pre = first_row['BCVA_pre']
    sphere = first_row['Sphere']
    cylinder = first_row['Cylinder']

if st.button("Calculate"):
    k1_post, k2_post = calculate_postop_k(k1_pre, k2_pre, sphere, cylinder)
    kavg_post = (k1_post + k2_post) / 2
    ablation_depth = 15 * (abs(sphere) + abs(cylinder)) if sphere <= 0 else 1 * (abs(sphere) + abs(cylinder))
    pachy_post = calculate_postop_pachymetry(pachy_pre, ablation_depth)
    bcva_post = calculate_postop_bcva(bcva_pre, sphere)
    surgery = determine_surgery(sphere, cylinder, pachy_pre, pachy_post, kavg_post, age)
    warnings = check_warnings((k1_pre + k2_pre)/2, pachy_pre, pachy_post, sphere, bcva_post)

    st.subheader("Calculated Results")
    st.write(f"**Post-op K1:** {round(k1_post, 2)} D")
    st.write(f"**Post-op K2:** {round(k2_post, 2)} D")
    st.write(f"**Post-op Kavg:** {round(kavg_post, 2)} D")
    st.write(f"**Post-op Pachymetry:** {round(pachy_post, 2)} µm")
    st.write(f"**Post-op BCVA:** {round(bcva_post, 2)}")
    st.write(f"**Recommended Surgery:** {surgery}")
    st.write(f"**Warnings:** {', '.join(warnings) if warnings else 'None'}")
