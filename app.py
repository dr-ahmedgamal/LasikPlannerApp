
import streamlit as st
import pandas as pd
from logic import calculate_postop_k, calculate_postop_pachymetry, calculate_postop_bcva, determine_surgery, check_warnings

st.title('LASIK Surgical Planner')

uploaded_file = st.file_uploader("Upload patient data CSV", type=["csv"])

if uploaded_file:
    data = pd.read_csv(uploaded_file)

    st.write("### Input Data")
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

        K1_post, K2_post = calculate_postop_k(K1_pre, K2_pre, sphere, cylinder)
        k_avg_post = (K1_post + K2_post) / 2
        ablation_depth = 15 * (abs(sphere) + abs(cylinder)) if sphere <= 0 else 1 * (abs(sphere) + abs(cylinder))
        pachy_post = calculate_postop_pachymetry(pachy_pre, ablation_depth)
        bcva_post = calculate_postop_bcva(bcva_pre, sphere)
        surgery = determine_surgery(sphere, cylinder, pachy_pre, pachy_post, k_avg_post, age)
        warnings = check_warnings((K1_pre + K2_pre)/2, pachy_pre, pachy_post, sphere, bcva_post)

        results.append({
            'PatientID': row['PatientID'],
            'Post-op K1': round(K1_post, 2),
            'Post-op K2': round(K2_post, 2),
            'Post-op Pachymetry': round(pachy_post, 2),
            'Post-op BCVA': round(bcva_post, 2),
            'Recommended Surgery': surgery,
            'Warnings': ', '.join(warnings) if warnings else 'None'
        })

    st.write("### Results")
    st.dataframe(pd.DataFrame(results))
else:
    st.info("Please upload a CSV file to start.")
