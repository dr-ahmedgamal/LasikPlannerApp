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


def app():
    st.title("LASIK & IOL Surgical Recommendation Tool")

    # Input cells arranged exactly as requested
    age = st.number_input("Age", min_value=18, max_value=100, value=18, step=1)
    sphere = st.number_input("Sphere (D)", value=0.00, step=0.25, format="%.2f")
    cylinder = st.number_input("Cylinder (D)", value=0.00, step=0.25, format="%.2f")
    bcva = st.number_input("BCVA (decimal)", min_value=0.0, max_value=2.0, value=1.0, step=0.01, format="%.2f")
    k1 = st.number_input("K1 (D)", min_value=30.0, max_value=60.0, value=43.00, step=0.1, format="%.2f")
    k2 = st.number_input("K2 (D)", min_value=30.0, max_value=60.0, value=44.00, step=0.1, format="%.2f")
    pachy = st.number_input("Pachymetry (µm)", min_value=300, max_value=700, value=520, step=1)
    optical_zone = st.number_input("Optical Zone (mm)", min_value=5.0, max_value=8.0, value=6.5, step=0.1, format="%.1f")

    st.markdown("")  # Small vertical space before upload section

    # Upload section header with smaller font
    st.markdown(
        '<p style="font-size:14px; font-weight:normal;">📝 Input Patient Data Manually or Upload a File</p>',
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader("", type=["csv", "txt"], help="Upload CSV or TXT file")

    # If file uploaded, read and override inputs with first row data
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_csv(uploaded_file, delimiter="\t")  # assume tab-delimited if txt
            if not df.empty:
                # Override inputs with first row values (if present)
                age = int(df.iloc[0].get("age", age))
                sphere = float(df.iloc[0].get("sphere", sphere))
                cylinder = float(df.iloc[0].get("cylinder", cylinder))
                bcva = float(df.iloc[0].get("bcva", bcva))
                k1 = float(df.iloc[0].get("k1", k1))
                k2 = float(df.iloc[0].get("k2", k2))
                pachy = float(df.iloc[0].get("pachymetry", pachy))
                optical_zone = float(df.iloc[0].get("optical_zone", optical_zone))
        except Exception as e:
            st.error(f"Error reading uploaded file: {e}")

    st.markdown("")  # small space before button

    # Larger Analyze and Recommend button
    if st.button("Analyze and Recommend", use_container_width=True):
        # Calculate postop K
        k1_post, k2_post = calculate_postop_k(k1, k2, sphere, cylinder)
        k_avg_post = round((k1_post + k2_post) / 2, 2)

        # Calculate postop pachymetry and ablation depth
        pachy_post, ablation_depth = calculate_postop_pachymetry(pachy, sphere, cylinder, optical_zone)

        # Calculate postop BCVA
        bcva_post = calculate_postop_bcva(bcva, sphere)

        # Determine surgery recommendation
        recommendation = determine_surgery(sphere, cylinder, pachy, pachy_post, k_avg_post, age)

        # Check warnings
        warnings = check_warnings(k_avg_post, pachy, pachy_post, sphere, bcva_post, cylinder)
        # Add postop k_avg warning
        if k_avg_post < 36 or k_avg_post > 49:
            warnings.append("Warning: Post-op K average out of range (36-49 D)")

        # Display results
        st.subheader("Results:")
        st.markdown(f"- **Post-op K1:** {k1_post} D")
        st.markdown(f"- **Post-op K2:** {k2_post} D")
        st.markdown(f"- **Post-op K Average:** {k_avg_post} D")
        st.markdown(f"- **Post-op Pachymetry:** {pachy_post} µm")
        st.markdown(f"- **Ablation Depth:** {ablation_depth} µm")
        st.markdown(f"- **Post-op BCVA:** {bcva_post}")
        st.markdown(f"- **Recommended Surgery:** {recommendation}")

        if warnings:
            st.warning("Warnings:")
            for w in warnings:
                st.write(f"- {w}")

if __name__ == "__main__":
    app()
