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

def process_case(age, sphere, cylinder, bcva, k1, k2, pachy, optical_zone):
    k1_post, k2_post = calculate_postop_k(k1, k2, sphere, cylinder)
    k_avg_post = round((k1_post + k2_post) / 2, 2)
    k_avg_pre = round((k1 + k2) / 2, 2)
    
    ablation_depth = calculate_ablation_depth(sphere, cylinder, optical_zone)
    pachy_post, _ = calculate_postop_pachymetry(pachy, sphere, cylinder, optical_zone)
    bcva_post = calculate_postop_bcva(bcva, sphere)
    
    recommended_surgery = determine_surgery(sphere, cylinder, pachy, pachy_post, k_avg_post, age, ablation_depth)
    warnings = check_warnings(k_avg_pre, pachy, pachy_post, sphere, bcva_post, cylinder)
    
    return {
        "Post-op K1": k1_post,
        "Post-op K2": k2_post,
        "Post-op K avg": k_avg_post,
        "Ablation Depth (µm)": ablation_depth,
        "Post-op Pachymetry (µm)": pachy_post,
        "Post-op BCVA": bcva_post,
        "Recommendation": recommended_surgery,
        "Warnings": warnings
    }

def main():
    st.title("LASIK Outcome Predictor & Refractive Surgery Recommender")

    st.markdown("### 🔧 Manual Input")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        age = st.number_input("Age (years)", min_value=10, max_value=100, value=18)
    with col2:
        sphere = st.number_input("Sphere (D)", value=0.00, step=0.25)
    with col3:
        cylinder = st.number_input("Cylinder (D)", value=0.00, step=0.25)
    with col4:
        bcva = st.number_input("BCVA (Decimal)", value=1.0, min_value=0.0, max_value=2.0, step=0.1)

    col5, col6, col7, col8 = st.columns(4)
    with col5:
        k1 = st.number_input("K1 (D)", value=43.0, step=0.1)
    with col6:
        k2 = st.number_input("K2 (D)", value=44.0, step=0.1)
    with col7:
        pachy = st.number_input("Pachymetry (µm)", value=520)
    with col8:
        optical_zone = st.number_input("Optical Zone (mm)", min_value=5.0, max_value=8.0, value=6.5, step=0.1)

    st.markdown("---")
    st.markdown("📝 *Optional: Upload CSV to Auto-Fill (overrides manual fields)*", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload CSV file (columns: age, sphere, cylinder, bcva, k1, k2, pachy, optical_zone)", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.success("CSV uploaded successfully. Showing predictions below:")

        results = []
        for _, row in df.iterrows():
            result = process_case(
                age=row["age"],
                sphere=row["sphere"],
                cylinder=row["cylinder"],
                bcva=row["bcva"],
                k1=row["k1"],
                k2=row["k2"],
                pachy=row["pachy"],
                optical_zone=row["optical_zone"]
            )
            results.append(result)

        result_df = pd.DataFrame(results)
        st.dataframe(result_df)

    st.markdown("---")
    if st.button("🔍 Analyze and Recommend Surgery"):
        result = process_case(age, sphere, cylinder, bcva, k1, k2, pachy, optical_zone)

        st.markdown("### ✅ Postoperative Calculations")
        st.write(f"**Post-op K1:** {result['Post-op K1']} D")
        st.write(f"**Post-op K2:** {result['Post-op K2']} D")
        st.write(f"**Post-op K average:** {result['Post-op K avg']} D")
        st.write(f"**Ablation Depth:** {result['Ablation Depth (µm)']} µm")
        st.write(f"**Post-op Pachymetry:** {result['Post-op Pachymetry (µm)']} µm")
        st.write(f"**Post-op BCVA:** {result['Post-op BCVA']}")

        st.markdown("### 📌 Surgical Recommendation")
        st.success(f"**{result['Recommendation']}**")

        if result["Warnings"]:
            st.markdown("### ⚠️ Warnings")
            for warning in result["Warnings"]:
                st.warning(warning)
        else:
            st.success("No warnings detected.")

if __name__ == "__main__":
    main()
