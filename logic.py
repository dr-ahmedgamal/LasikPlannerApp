# logic.py

import math

def calculate_spherical_equivalent(sphere, cylinder):
    return round(sphere + (cylinder / 2), 2)

def calculate_ablation_depth(se, optical_zone):
    """
    Munnerlyn formula adjusted by a correction factor of 1.1:
    Ablation Depth (µm) = (OZ^2 × |SE| / 3) × 1.1
    """
    ablation_depth = ((optical_zone ** 2) * abs(se) / 3) * 1.1
    return round(ablation_depth, 2)

def calculate_postop_pachymetry(preop_pachy, ablation_depth, is_myopic=True):
    """
    For myopia: postop_pachy = preop - ablation_depth
    For hyperopia: postop_pachy = preop - 6µm (fixed)
    """
    if is_myopic:
        return round(preop_pachy - ablation_depth, 2)
    else:
        return round(preop_pachy - 6, 2)

def calculate_delta_K(sphere, cylinder):
    abs_sphere = abs(sphere)
    abs_cyl = abs(cylinder)

    if sphere < 0:  # Myopia
        delta_K1 = abs_sphere * 0.8
        delta_K2 = (abs_sphere + abs_cyl) * 0.8
    else:  # Hyperopia
        delta_K1 = abs_sphere * 1.2
        delta_K2 = (abs_sphere - abs_cyl) * 1.2
        if delta_K2 < 0:
            delta_K2 = 0

    return round(delta_K1, 2), round(delta_K2, 2)

def calculate_postop_K(K1_pre, K2_pre, delta_K1, delta_K2, is_myopic=True):
    if is_myopic:
        K1_post = K1_pre - delta_K1
        K2_post = K2_pre - delta_K2
    else:
        K1_post = K1_pre + delta_K1
        K2_post = K2_pre + delta_K2
    Kavg_post = (K1_post + K2_post) / 2
    return round(K1_post, 2), round(K2_post, 2), round(Kavg_post, 2)

def check_alerts(Kmax, preop_pachy, postop_pachy, se, bcva):
    alerts = []

    if Kmax > 49 and preop_pachy < 500:
        alerts.append("⚠️ Keratoconus Risk: K > 49 D and pachymetry < 500 µm")

    if postop_pachy < 410:
        alerts.append("⚠️ Ectasia Risk: Post-op pachymetry < 410 µm")

    if se > 6:
        alerts.append("❗ Extreme Hyperopia: SE > +6 D")

    if se < -12:
        alerts.append("❗ Extreme Myopia: SE < -12 D")

    if bcva < 0.5:
        alerts.append("❗ Low Visual Potential: BCVA < 0.5")

    return alerts

def recommend_procedure(age, se, preop_pachy, postop_pachy, Kavg_post, ablation_depth):
    recommendations = []

    # LASIK eligibility
    if (
        preop_pachy >= 500 and
        postop_pachy >= 410 and
        34 <= Kavg_post <= 50 and
        ablation_depth <= 140
    ):
        recommendations.append("LASIK")

    # PRK eligibility
    if (
        se < 0 and
        preop_pachy >= 460 and
        postop_pachy >= 400 and
        34 <= Kavg_post <= 50 and
        ablation_depth <= 90
    ):
        recommendations.append("PRK")

    # Phakic IOL
    if (se <= -10 or se >= +7 or preop_pachy < 460 or Kavg_post < 34 or Kavg_post > 50):
        if age < 40:
            recommendations.append("Phakic IOL")
        else:
            recommendations.append("Pseudophakic IOL")

    # Final logic for output
    if "LASIK" in recommendations and "PRK" in recommendations:
        return "LASIK / PRK"
    elif recommendations:
        return recommendations[0]
    else:
        return "No Suitable Procedure"

def run_full_analysis(
    sphere, cylinder, optical_zone, preop_pachy, K1_pre, K2_pre, Kmax, bcva, age
):
    se = calculate_spherical_equivalent(sphere, cylinder)
    ablation_depth = calculate_ablation_depth(se, optical_zone)

    is_myopic = sphere < 0
    postop_pachy = calculate_postop_pachymetry(preop_pachy, ablation_depth, is_myopic)
    delta_K1, delta_K2 = calculate_delta_K(sphere, cylinder)
    K1_post, K2_post, Kavg_post = calculate_postop_K(K1_pre, K2_pre, delta_K1, delta_K2, is_myopic)
    alerts = check_alerts(Kmax, preop_pachy, postop_pachy, se, bcva)
    recommendation = recommend_procedure(age, se, preop_pachy, postop_pachy, Kavg_post, ablation_depth)

    return {
        "SE": se,
        "Ablation Depth (µm)": ablation_depth,
        "Post-op Pachymetry (µm)": postop_pachy,
        "Delta K1": delta_K1,
        "Delta K2": delta_K2,
        "Post-op K1": K1_post,
        "Post-op K2": K2_post,
        "Post-op Kavg": Kavg_post,
        "Alerts": alerts,
        "Recommendation": recommendation
    }
