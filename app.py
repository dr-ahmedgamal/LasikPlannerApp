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

    # Input cells arranged as requested
    age = st.number_input("Age", min_value=18, max_value=100, value=18, step=1)
    sphere = st.number_input("Sphere (D)", value=0.00, step=0.25, format="%.2f")
    cylinder = st.number_input("Cylinder (D)", value=0.00, step=0.25, format="%.2f")
    bcva = st.number_input("BCVA (decimal)", min_value=0.0, max_value=2.0, value=1.0, step=0.01, format="%.2f")
    k1 = st.number_input("K1 (D)", min_value=30.0, max_value=60.0, value=43.00, step=0.1, format="%.2f")
    k2 = st.number_input("K2 (D)", min_value=30.0, max_value=60.0, value=44.00, step=0.1, format="%.2f")
    pachy = st.number_input("Pachymetry (µm)", min_value=300, max_value=700, value=520, step=1)
    optical_zone = st.number_input("Optical Zone (mm)", min_value=5.0, max_value=8.0, value=6.5, step=0.1, format="%.1f")

    # Spacer before upload
    st.write("")
    st.write("")
    st.write("")

    # Upload section with smaller header font and minimal text, close to uploader
    st.markdown(
        '<p style="font-size:14px; font-weight:normal; margin-bottom: 4px;">📝 Input Data Manually or Upload File</p>',
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader("", type=["csv", "txt"], help="Upload CSV or TXT file")

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_csv(uploaded_file, delimiter="\t")
            if not df.empty:
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

    # Small spacer before button
    st.write("")
    st.write("")

    # Style for the big blue medical button
    st.markdown(
        """
        <style>
        div.stButton > button {
            background-color: #007ACC;
            color: white;
            font-size: 22px;
            font-weight: bold;
            padding: 15px 0;
            border-radius: 10px;
            width: 100%;
            transition: background-color 0.3s ease;
            border: none;
            cursor: pointer;
        }
        div.stButton > button:hover {
            background-color: #005A9E;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Single analyze button
    if st.button("Analyze and Recommend"):
        k1_post, k2_post = calculate_postop_k(k1, k2, sphere, cylinder)
        k_avg_post = round((k1_post + k2_post) / 2, 2)

        pachy_post, ablation_depth = calculate_postop_pachymetry(pachy, sphere, cylinder, optical_zone)

        bcva_post = calculate_postop_bcva(bcva, sphere)

        recommendation = determine_surgery(sphere, cylinder, pachy, pachy_post, k_avg_post, age)

        warnings = check_warnings(k_avg_post, pachy, pachy_post, sphere, bcva_post, cylinder)

        # Add postop K average warning
        if k_avg_post < 36 or k_avg_post > 49:
            warnings.append("Warning: Post-op K average out of range (36-49 D)")

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
