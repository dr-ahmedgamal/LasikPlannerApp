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
    "<h2 style='color:#1f77b4;'>👁️ Refractive Surgery AI Planner</h2>",
    unsafe_allow_html=True,
)

# --- Input Section ---
st.markdown("### 👇 Enter Patient Data")

col1, col2, col3, col4 = st.columns(4)
with col1:
    age = st.number_input("Age", min_value=18, max_value=100, value=18)
with col2:
    sphere = st.number_input("Sphere (D)", step=0.25, value=0.00)
with col3:
    cylinder = st.number_input("Cylinder (D)", step=0.25, value=0.00)
with col4:
    bcva_pre = st.number_input("BCVA", step=0.1, value=1.0)

col5, col6, col7, col8 = st.columns(4)
with col5:
    k1_pre = st.number_input("K1 (D)", step=0.1, value=42.0)
with col6:
    k2_pre = st.number_input("K2 (D)", step=0.1, value=43.0)
with col7:
    pachy_pre = st.number_input("Pachymetry (µm)", step=1, value=520)
with col8:
    optical_zone = st.number_input("Optical Zone (mm)", step=0.1, value=6.5)

# --- Spacer between input and upload ---
st.markdown("<br>", unsafe_allow_html=True)

# --- Upload Section ---
st.markdown("<p style='font-size: 16px;'>Upload Patient Data (optional)</p>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=["csv", "txt"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if not df.empty:
        row = df.iloc[0]
        age = row.get("age", age)
        sphere = row.get("sphere", sphere)
        cylinder = row.get("cylinder", cylinder)
        bcva_pre = row.get("bcva", bcva_pre)
        k1_pre = row.get("k1", k1_pre)
        k2_pre = row.get("k2", k2_pre)
        pachy_pre = row.get("pachymetry", pachy_pre)
        optical_zone = row.get("optical_zone", optical_zone)

# --- Extra spacing before button ---
st.markdown("<br><br>", unsafe_allow_html=True)

# --- Very Large Centered Button ---
button_container = st.columns([1, 2, 1])[1]
with button_container:
    clicked = st.button(
        "🧠 Refractive Plan",
        use_container_width=True,
        key="refractive_plan",
    )
    st.markdown(
        """
        <style>
            div[data-testid="stButton"] button {
                font-size: 22px !important;
                height: 60px !important;
                font-weight: bold;
                background-color: #007BFF;
                color: white;
                border-radius: 8px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

# --- Results Section ---
if clicked:
    k1_post, k2_post = calculate_postop_k(k1_pre, k2_pre, sphere, cylinder)
    k_avg_post = round((k1_post + k2_post) / 2, 2)
    pachy_post, ablation_depth = calculate_postop_pachymetry(pachy_pre, sphere, cylinder, optical_zone)
    bcva_post = calculate_postop_bcva(bcva_pre, sphere)
    surgery = determine_surgery(sphere, cylinder, pachy_pre, pachy_post, k_avg_post, age)
    warnings = check_warnings((k1_pre + k2_pre) / 2, pachy_pre, pachy_post, sphere, bcva_post, cylinder)

    st.markdown("---")
    st.subheader("🔍 Results")
    st.write(f"**Post-op K1:** {k1_post} D")
    st.write(f"**Post-op K2:** {k2_post} D")
    st.write(f"**Post-op K_avg:** {k_avg_post} D")
    st.write(f"**Ablation Depth:** {ablation_depth} µm")
    st.write(f"**Post-op Pachymetry:** {pachy_post} µm")
    st.write(f"**Post-op BCVA:** {bcva_post}")
    st.write(f"### ✅ Recommended Procedure: {surgery}")

    if warnings:
        st.warning("⚠️ " + "\n\n".join(warnings))
