import streamlit as st
from logic import (
    calculate_postop_k,
    calculate_ablation_depth,
    calculate_postop_pachymetry,
    calculate_postop_bcva,
    determine_surgery,
    check_warnings,
)

def main():
    st.title("LASIK Outcome Prediction & Surgical Recommendation")

    # Input fields
    k1_pre = st.number_input("Pre-op K1 (D)", value=43.0)
    k2_pre = st.number_input("Pre-op K2 (D)", value=44.0)
    sphere = st.number_input("Sphere (D)", value=-4.0)
    cylinder = st.number_input("Cylinder (D)", value=-1.0)
    pachy_pre = st.number_input("Pre-op Pachymetry (µm)", value=540)
    bcva_pre = st.number_input("Pre-op BCVA (Decimal, e.g. 1.0)", value=1.0, min_value=0.0, max_value=2.0)
    age = st.number_input("Age (years)", min_value=10, max_value=100, value=30)
    optical_zone = st.number_input("Optical Zone (mm)", min_value=5.0, max_value=8.0, value=6.5)

    if st.button("Calculate Outcomes and Recommend Surgery"):
        # Calculate post-op K values
        k1_post, k2_post = calculate_postop_k(k1_pre, k2_pre, sphere, cylinder)
        k_avg_post = round((k1_post + k2_post) / 2, 2)
        k_avg_pre = round((k1_pre + k2_pre) / 2, 2)

        # Calculate ablation depth
        ablation_depth = calculate_ablation_depth(sphere, cylinder, optical_zone)

        # Calculate post-op pachymetry
        pachy_post, _ = calculate_postop_pachymetry(pachy_pre, sphere, cylinder, optical_zone)

        # Calculate post-op BCVA
        bcva_post = calculate_postop_bcva(bcva_pre, sphere)

        # Determine surgery recommendation
        recommended_surgery = determine_surgery(sphere, cylinder, pachy_pre, pachy_post, k_avg_post, age, ablation_depth)

        # Warnings
        warnings = check_warnings(k_avg_pre, pachy_pre, pachy_post, sphere, bcva_post, cylinder)

        # Display results
        st.subheader("Postoperative Outcomes:")
        st.write(f"Post-op K1: {k1_post} D")
        st.write(f"Post-op K2: {k2_post} D")
        st.write(f"Post-op K average: {k_avg_post} D")
        st.write(f"Ablation Depth: {ablation_depth} µm")
        st.write(f"Post-op Pachymetry: {pachy_post} µm")
        st.write(f"Post-op BCVA (Decimal): {bcva_post}")

        st.subheader("Surgical Recommendation:")
        st.write(f"**{recommended_surgery}**")

        if warnings:
            st.subheader("Warnings & Notes:")
            for warning in warnings:
                st.warning(warning)
        else:
            st.success("No warnings detected.")

if __name__ == "__main__":
    main()
