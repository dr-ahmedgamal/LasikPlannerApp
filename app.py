# app.py

import streamlit as st
from logic import run_full_analysis

st.set_page_config(page_title="LASIK Surgical Recommendation & Calculator", layout="centered")

st.title("🔷 LASIK Surgical Recommendation & Calculation Tool")

st.markdown("""
This app calculates the recommended refractive surgery based on patient data,
including corneal measurements and refractive errors, following the latest clinical guidelines.
""")

# --- Input Section ---
st.header("Patient Data Input")

col1, col2 = st.columns(2)

with col1:
    sphere = st.number_input("Sphere (D)", value=0.0, format="%.2f", step=0.25,
                             help="Enter spherical refraction in diopters (negative for myopia, positive for hyperopia)")
    cylinder = st.number_input("Cylinder (D)", value=0.0, format="%.2f", step=0.25,
                               help="Enter cylindrical refraction in diopters (astigmatism)")
    optical_zone = st.number_input("Optical Zone (mm)", min_value=5.0, max_value=8.0, value=6.0, step=0.1,
                                   help="Enter optical zone diameter for ablation calculation")

with col2:
    preop_pachy = st.number_input("Preoperative Pachymetry (µm)", min_value=300, max_value=700, value=540,
                                  help="Central corneal thickness before surgery")
    K1_pre = st.number_input("Preoperative K1 (D)", min_value=30.0, max_value=60.0, value=43.0, step=0.1,
                             help="Flat keratometry reading")
    K2_pre = st.number_input("Preoperative K2 (D)", min_value=30.0, max_value=60.0, value=44.0, step=0.1,
                             help="Steep keratometry reading (important for ectasia risk)")

age = st.number_input("Patient Age (years)", min_value=10, max_value=100, value=28,
                      help="Age of patient to determine lens implant suitability")
bcva = st.number_input("Best Corrected Visual Acuity (BCVA, decimal)", min_value=0.1, max_value=1.5, value=1.0, step=0.1,
                       help="Decimal value for BCVA (e.g. 1.0 = 20/20)")

# --- Run Analysis ---
if st.button("Calculate Recommendation"):
    with st.spinner("Calculating..."):
        results = run_full_analysis(
            sphere=sphere,
            cylinder=cylinder,
            optical_zone=optical_zone,
            preop_pachy=preop_pachy,
            K1_pre=K1_pre,
            K2_pre=K2_pre,
            bcva=bcva,
            age=age
        )

    st.subheader("Calculation Results")

    st.write(f"**Ablation Depth:** {results['Ablation Depth (µm)']} µm")
    st.write(f"**Postoperative Pachymetry:** {results['Post-op Pachymetry (µm)']} µm")
    st.write(f"**Postoperative Average K:** {results['Post-op Kavg']} D")
    st.write(f"**Predicted Postoperative UCVA:** {results.get('Predicted Post-op UCVA', 'N/A')}")

    if results["Alerts"]:
        st.warning("⚠️ **Alerts & Warnings:**")
        for alert in results["Alerts"]:
            st.write(f"- {alert}")
    else:
        st.success("✅ No alerts or warnings detected.")

    st.markdown("---")
    st.header("Surgical Recommendation")

    # Adjusted recommendation logic display:
    rec = results["Recommendation"]

    # Handle combined recommendations logic:
    if isinstance(rec, list) and len(rec) > 1:
        # Prioritize LASIK first
        if "LASIK" in rec:
            rec_sorted = ["LASIK"] + [r for r in rec if r != "LASIK"]
            rec_str = " / ".join(rec_sorted)
        else:
            rec_str = " / ".join(rec)
    else:
        rec_str = rec if isinstance(rec, str) else ", ".join(rec)

    st.info(f"**Recommended Procedure:** {rec_str}")

    st.markdown("""
    ---
    **Notes:**
    - Recommendations are based on current clinical guidelines.
    - Always correlate with clinical examination and patient-specific factors.
    """)

else:
    st.info("Enter patient data and click 'Calculate Recommendation' to see the results.")
