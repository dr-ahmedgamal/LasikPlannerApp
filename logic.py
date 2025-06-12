# logic.py

def munnerlyn_formula(sphere, cylinder, optical_zone):
    """
    Calculate ablation depth using Munnerlyn formula corrected by 1.1 factor.
    Inputs:
      - sphere, cylinder: absolute diopters
      - optical_zone: in mm
    Returns:
      - ablation depth in microns (float)
    """
    total_diopters = abs(sphere) + abs(cylinder)
    ablation_depth = 1.1 * (total_diopters * (optical_zone ** 2) / 3)
    return round(ablation_depth, 2)


def calculate_postop_pachymetry(preop_pachy, ablation_depth, sphere):
    """
    Calculate postoperative pachymetry.
    For myopia (sphere <= 0), subtract ablation depth.
    For hyperopia (sphere > 0), subtract fixed 6 µm.
    """
    if sphere <= 0:
        postop = preop_pachy - ablation_depth
    else:
        postop = preop_pachy - 6
    return round(postop, 2)


def calculate_delta_K(sphere, cylinder):
    """
    Calculate changes in corneal curvature ΔK1 and ΔK2.
    Clamp ΔK2 in hyperopia to minimum zero.
    """
    abs_sphere = abs(sphere)
    abs_cyl = abs(cylinder)

    if sphere <= 0:
        delta_K1 = abs_sphere * 0.8
        delta_K2 = (abs_sphere + abs_cyl) * 0.8
    else:
        delta_K1 = abs_sphere * 1.2
        delta_K2 = (abs_sphere - abs_cyl) * 1.2
        if delta_K2 < 0:
            delta_K2 = 0

    return round(delta_K1, 2), round(delta_K2, 2)


def calculate_postop_K(K1_pre, K2_pre, sphere, cylinder):
    delta_K1, delta_K2 = calculate_delta_K(sphere, cylinder)

    if sphere <= 0:
        K1_post = K1_pre - delta_K1
        K2_post = K2_pre - delta_K2
    else:
        K1_post = K1_pre + delta_K1
        K2_post = K2_pre + delta_K2

    return round(K1_post, 2), round(K2_post, 2)

def predict_postop_uava(bcva, sphere):
    """
    Predict postoperative uncorrected VA (Post-op UAVA) based on sphere correction.
    - If myopia (sphere <= 0): UAVA = BCVA + 0.05 * abs(sphere), capped at 1.2
    - If hyperopia or emmetropia: UAVA = BCVA
    """
    if sphere < 0:
        improvement = 0.05 * abs(sphere)
        uava = bcva + improvement
    else:
        uava = bcva

    # Ensure UAVA does not exceed max limit
    uava = min(uava, 1.2)

    return round(uava, 2)

def run_full_analysis(sphere, cylinder, optical_zone, preop_pachy, K1_pre, K2_pre, bcva, age):
    """
    Main analysis function returning results dictionary including alerts and recommendations.
    """

    results = {}

    ablation_depth = munnerlyn_formula(sphere, cylinder, optical_zone)
    postop_pachy = calculate_postop_pachymetry(preop_pachy, ablation_depth, sphere)

    K1_post, K2_post = calculate_postop_K(K1_pre, K2_pre, sphere, cylinder)
    postop_Kavg = round((K1_post + K2_post) / 2, 2)

    # Predict postoperative uncorrected VA (Post-op UAVA) based on sphere correction.
    # - If sphere <= 0: Post-op UAVA = BCVA + 0.05 * abs(sphere), capped at 1.2
    # - If sphere > 0: Post-op UAVA = BCVA

    results["Ablation Depth (µm)"] = ablation_depth
    results["Post-op Pachymetry (µm)"] = postop_pachy
    results["Post-op Kavg"] = postop_Kavg
    results["BCVA"] = bcva
    results["Predicted Post-op UAVA"] = predict_postop_uava(bcva, sphere)
    uava = predict_postop_uava(bcva, sphere)
    results["Predicted Post-op UAVA"] = uava

    alerts = []

    # Alerts & Warnings
    if  K2_pre > 48 and preop_pachy < 500:
        alerts.append("Keratoconus risk:  K2_pre > 49 D and pachymetry < 500 µm")

    if postop_pachy < 400:
        alerts.append("Ectasia risk: postoperative pachymetry < 410 µm")

    if sphere > 6:
        alerts.append("Extreme hyperopia: SE > +6 D")

    if sphere < -12:
        alerts.append("Extreme myopia: SE < -12 D")

    if uava < 0.5:
        alerts.append("Low visual potential: BCVA < 0.5")

    results["Alerts"] = alerts

    # Eligibility checks
    lasik_eligible = (
        preop_pachy >= 500 and
        postop_pachy >= 410 and
        34 <= postop_Kavg <= 50 and
        ablation_depth <= 150
    )

    prk_eligible = (
        sphere < 0 and
        preop_pachy >= 460 and
        postop_pachy >= 400 and
        ablation_depth <= 100 and
        34 <= postop_Kavg <= 50
    )

    # UPDATED eligibility conditions as requested
    phakic_iol_eligible = ( 
        age < 40 and
        (sphere <= -8 or sphere > +6 or postop_pachy < 400) 
    )

    pseudophakic_iol_eligible = (
        age >= 40 and
        (sphere <= -8 or sphere > +6 or postop_pachy < 400)
    )

    
    recommendations = []

    if lasik_eligible:
        recommendations.append("LASIK")
    if prk_eligible:
        recommendations.append("PRK")
    if phakic_iol_eligible:
        recommendations.append("Phakic IOL")
    if pseudophakic_iol_eligible:
        recommendations.append("Pseudophakic IOL")

    # Ensure LASIK is always first if present
    if "LASIK" in recommendations:
        recommendations = ["LASIK"] + [r for r in recommendations if r != "LASIK"]

    if len(recommendations) > 1:
        results["Recommendation"] = recommendations
    elif len(recommendations) == 1:
        results["Recommendation"] = recommendations[0]
    else:
        results["Recommendation"] = "No suitable surgical option based on input data."

    return results
