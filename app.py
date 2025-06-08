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

# Input fields in the requested order
age = st.number_input("Age", min_value=0, value=18, step=1)
sphere = st.number_input("Sphere (D)", value=0.00, step=0.25, format="%.2f")
cylinder = st.number_input("Cylinder (D)", value=0.00, step=0.25, format="%.2f")
bcva_pre = st.number_input("BCVA (LogMAR)", value=1.0, step=0.01, format="%.2f")
k1_pre = st.number_input("K1 (D)", value=43.00, step=0.01, format="%.2f")
k2_pre = st.number_input("K2 (D)", value=44.00, step=0.01, format="%.2f")
pachy_pre = st.number_input("Pre-op Pachymetry (µm)", value=540, step=1)
optical_zone = st.number_input("Optical Zone (mm)", value=6.5, step=0.1, format="%.2f")

# Custom CSS to enlarge the font size of the upload label slightly
st.markdown(
    """
    <style>
    .upload-label {
        font-size: 0.9rem;
        font-weight: 600;
        margin-top: 1em;
        margin-bottom: 0.3em;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="upload-label">Optional: Upload CSV to Auto-Fill (overrides manual fields)</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type=["csv"])

if uploaded_file:
    data = pd.read_csv(uploaded_file)
    st.write("### Input Data from CSV")
    st.dataframe(data)

    results = []
    for idx, row in data.iterrows():
        sphere = row['Sphere']
        cylinder = row['Cylinder']
        K1_pre = row['K1_pre']
        K2_pre = row['K2_pre']
        pachy_pre = row['Pachymetry_pre']
        bcva_pre = row['BCVA_pre']
        age = row['Age']
        optical_zone = row.get('OpticalZone', optical_zone)  # fallback to manual input if not in CSV

        K1_post, K2_post = calculate_postop_k(K1_pre, K2_pre, sphere, cylinder)
        k_avg_post = (K1_post + K2_post) / 2
        ablation_depth = 1.1 * (3 * optical_zone ** 2) * (abs(sphere) + abs(cylinder))
        pachy_post = calculate_postop_pachymetry(pachy_pre, ablation_depth, sphere)
        bcva_post = calculate_postop_bcva(bcva_pre, sphere + cylinder)
        surgery = determine_surgery(sphere, cylinder, pachy_pre, pachy_post, k_avg_post, age)
        warnings = check_warnings((K1_pre + K2_pre) / 2, pachy_pre, pachy_post, sphere, bcva_post, cylinder)

        results.append({
            'PatientID': row.get('PatientID', idx + 1),
            'Post-op K1': round(K1_post, 2),
            'Post-op K2': round(K2_post, 2),
            'Post-op Kavg': round(k_avg_post, 2),
            'Ablation Depth (µm)': round(ablation_depth, 2),
            'Post-op Pachymetry': round(pachy_post, 2),
            'Post-op BCVA': round(bcva_post, 2),
            'Recommended Surgery': surgery,
            'Warnings': ', '.join(warnings) if warnings else 'None'
        })

    st.write("### Results")
    st.dataframe(pd.DataFrame(results))

else:
    st.write("### Manual Input Results")
    K1_post, K2_post = calculate_postop_k(k1_pre, k2_pre, sphere, cylinder)
    k_avg_post = (K1_post + K2_post) / 2
    ablation_depth = 1.1 * (3 * optical_zone ** 2) * (abs(sphere) + abs(cylinder))
    pachy_post = calculate_postop_pachymetry(pachy_pre, ablation_depth, sphere)
    bcva_post = calculate_postop_bcva(bcva_pre, sphere + cylinder)
    surgery = determine_surgery(sphere, cylinder, pachy_pre, pachy_post, k_avg_post, age)
    warnings = check_warnings((k1_pre + k2_pre) / 2, pachy_pre, pachy_post, sphere, bcva_post, cylinder)

    results = {
        'Post-op K1': round(K1_post, 2),
        'Post-op K2': round(K2_post, 2),
        'Post-op Kavg': round(k_avg_post, 2),
        'Ablation Depth (µm)': round(ablation_depth, 2),
        'Post-op Pachymetry': round(pachy_post, 2),
        'Post-op BCVA': round(bcva_post, 2),
        'Recommended Surgery': surgery,
        'Warnings': ', '.join(warnings) if warnings else 'None'
    }

    st.dataframe(pd.DataFrame([results]))
