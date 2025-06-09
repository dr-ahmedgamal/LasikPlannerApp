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
    For myopia (sphere < 0), subtract ablation depth.
    For hyperopia (sphere > 0), subtract fixed 6 µm.
    """
    if sphere < 0:
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

    if sphere < 0:
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

    if sphere < 0:
        K1_post = K1_pre - delta_K1
        K2_post = K2_pre - delta_K2
    else:
        K1_post = K1_pre + delta_K1
        K2_post = K2_pre + delta_K2

    return round(K1_post, 2), round(K2_post, 2)


def run_full_analysis(sphere, cylinder, optical_zone, preop_pachy, K1_pre, K2_pre, Kmax, bcva, age):
    """
    Main analysis function returning results dictionary including alerts and recommendations.
    """

    results = {}

    ablation_depth = munnerlyn_formula(sphere, cylinder, optical_zone)
    postop_pachy = calculate_postop_pachymetry(preop_pachy, ablation_depth, sphere)

    K1_post, K2_post = calculate_postop_K(K1_pre, K2_pre, sphere, cylinder)
    postop_Kavg = round((K1_post + K2_post) / 2, 2)

    results["Ablation Depth (µm)"] = ablation_depth
    results["Post-op Pachymetry (µm)"] = postop_pachy
    results["Post-op Kavg"] = postop_Kavg
    results["BCVA"] = bcva

    alerts = []

    # Alerts & Warnings
    if Kmax > 49 and preop_pachy < 500:
        alerts.append("Keratoconus risk: Kmax > 49 D and pachymetry < 500 µm")

    if postop_pachy < 410:
        alerts.append("Ectasia risk: postoperative pachymetry < 410 µm")

    if sphere > 6:
        alerts.append("Extreme hyperopia: SE > +6 D")

    if sphere < -12:
        alerts.append("Extreme myopia: SE < -12 D")

    if bcva < 0.5:
        alerts.append("Low visual potential: BCVA < 0.5")

    results["Alerts"] = alerts

    # Eligibility checks
    lasik_eligible = (
        preop_pachy >= 500 and
        postop_pachy >= 410 and
        34 <= postop_Kavg <= 50 and
        ablation_depth <= 140
    )

    prk_eligible = (
        sphere < 0 and
        preop_pachy >= 460 and
        postop_pachy >= 400 and
        ablation_depth <= 90 and
        34 <= postop_Kavg <= 50
    )

    phakic_iol_eligible = (
        age < 40 and
        not (lasik_eligible or prk_eligible) and
        (sphere <= -10 or preop_pachy < 500)
    )

    pseudophakic_iol_eligible = (
        age >= 40 and
        not (lasik_eligible or prk_eligible) and
        (sphere <= -10 or preop_pachy < 500)
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

    # Combined recommendation logic with LASIK prioritized
    if "LASIK" in recommendations:
        # Combine LASIK with others if applicable
        combined = ["LASIK"] + [r for r in recommendations if r != "LASIK"]
        results["Recommendation"] = combined if len(combined) > 1 else "LASIK"
    else:
        # No LASIK, just list whatever is eligible
        if recommendations:
            results["Recommendation"] = recommendations if len(recommendations) > 1 else recommendations[0]
        else:
            results["Recommendation"] = "No suitable surgical option based on input data."

    return results
