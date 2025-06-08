import streamlit as st
from logic import calculate_postop_k, calculate_postop_pachymetry, calculate_postop_bcva, determine_surgery, check_warnings

st.set_page_config(page_title="LASIK Surgical Planner", layout="centered")
st.title("LASIK Surgical Planner")

with st.form("input_form"):
    col1, col2 = st.columns(2)
    with col1:
        sphere = st.number_input("Sphere (D)", value=-3.00, step=0.25)
        cylinder = st.number_input("Cylinder (D)", value=-1.25, step=0.25)
        k1_pre = st.number_input("Pre-op K1 (D)", value=43.0)
        k2_pre = st.number_input("Pre-op K2 (D)", value=44.5)
    with col2:
        bcva_pre = st.number_input("Pre-op BCVA", min_value=0.0, max_value=1.5, value=0.8)
        pachy_pre = st.number_input("Pre-op Pachymetry (µm)", value=520.0)
        age = st.number_input("Age", min_value=10, max_value=90, value=28)

    submitted = st.form_submit_button("Calculate")

if submitted:
    # Run calculations
    k1_post, k2_post = calculate_postop_k(k1_pre, k2_pre, sphere, cylinder)
    k_avg_post = (k1_post + k2_post) / 2
    ablation_depth = 15 * (abs(sphere) + abs(cylinder)) if sphere <= 0 else 1 * (abs(sphere) + abs(cylinder))
    pachy_post = calculate_postop_pachymetry(pachy_pre, ablation_depth)
    bcva_post = calculate_postop_bcva(bcva_pre, sphere)
    surgery = determine_surgery(sphere, cylinder, pachy_pre, pachy_post, k_avg_post, age)
    warnings = check_warnings((k1_pre + k2_pre)/2, pachy_pre, pachy_post, sphere, bcva_post)

    st.subheader("📊 Results")
    st.markdown(f"**Post-op K1:** {round(k1_post, 2)} D")
    st.markdown(f"**Post-op K2:** {round(k2_post, 2)} D")
    st.markdown(f"**Post-op Kavg:** {round(k_avg_post, 2)} D")
    st.markdown(f"**Post-op Pachymetry:** {round(pachy_post, 2)} µm")
    st.markdown(f"**Post-op BCVA:** {round(bcva_post, 2)}")
    st.markdown(f"**Recommended Surgery:** `{surgery}`")

    if warnings:
        st.error("⚠ Warnings:\n" + "\n".join(f"- {w}" for w in warnings))
    else:
        st.success("✅ No warnings.")
