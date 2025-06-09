def calculate_postop_k(k1_pre, k2_pre, sphere, cylinder):
    """
    Calculate post-op K1 and K2 using latest formulas.

    Myopia:
        ΔK1 = |Sphere| × 0.8
        ΔK2 = (|Sphere| + |Cylinder|) × 0.8
        Post-op = Pre-op - ΔK

    Hyperopia:
        ΔK1 = |Sphere| × 1.2
        ΔK2 = (|Sphere| - |Cylinder|) × 1.2
        Post-op = Pre-op + ΔK
    """
    abs_sphere = abs(sphere)
    abs_cylinder = abs(cylinder)

    if sphere < 0:  # Myopia
        delta_k1 = abs_sphere * 0.8
        delta_k2 = (abs_sphere + abs_cylinder) * 0.8
        k1_post = k1_pre - delta_k1
        k2_post = k2_pre - delta_k2
    else:  # Hyperopia
        delta_k1 = abs_sphere * 1.2
        delta_k2 = (abs_sphere - abs_cylinder) * 1.2
        k1_post = k1_pre + delta_k1
        k2_post = k2_pre + delta_k2

    return round(k1_post, 2), round(k2_post, 2)


def calculate_ablation_depth(sphere, cylinder, optical_zone):
    """
    Munnerlyn formula with 1.1 correction factor:
    Ablation Depth = 1.1 × (Optical Zone² / 3) × (|Sphere| + |Cylinder|)
    """
    abs_sphere = abs(sphere)
    abs_cylinder = abs(cylinder)
    ablation_depth = 1.1 * ((optical_zone ** 2) / 3) * (abs_sphere + abs_cylinder)
    return round(ablation_depth, 2)


def calculate_postop_pachymetry(pachy_pre, sphere, cylinder, optical_zone):
    """
    Post-op pachymetry:
    - Myopia: subtract ablation depth
    - Hyperopia: subtract fixed 6 µm
    """
    ablation_depth = calculate_ablation_depth(sphere, cylinder, optical_zone)
    if sphere < 0:  # Myopia
        pachy_post = pachy_pre - ablation_depth
    else:  # Hyperopia
        pachy_post = pachy_pre - 6

    return round(pachy_post, 2), ablation_depth


def calculate_postop_bcva(bcva_pre, sphere):
    """
    Estimate BCVA:
    BCVA_post = min(BCVA_pre + |SE| × 0.05, 1.5)
    """
    abs_sphere = abs(sphere)
    bcva_post = bcva_pre + (abs_sphere * 0.05)
    return round(min(bcva_post, 1.5), 2)


def determine_surgery(sphere, cylinder, pachy_pre, pachy_post, k_avg_post, age, ablation_depth):
    """
    Revised logic for surgical recommendation:
    - LASIK and PRK eligibility as primary options
    - Phakic/Pseudophakic IOL fallback if LASIK/PRK ineligible
    """
    se = sphere + (cylinder / 2)
    abs_se = abs(se)
    abs_cylinder = abs(cylinder)

    lasik = (
        pachy_pre >= 500
        and pachy_post >= 410
        and (36 <= k_avg_post <= 49)
        and ablation_depth <= 140
    )

    prk = (
        se < 0
        and pachy_pre >= 460
        and pachy_post >= 400
        and (36 <= k_avg_post <= 49)
        and ablation_depth <= 90
    )

    phakic = (
        not lasik and not prk
        and se <= -10
        and age < 40
    )

    pseudophakic = (
        not lasik and not prk
        and se <= -10
        and age >= 40
    )

    # Recommendation logic based on combination
    if lasik and prk:
        return "LASIK / PRK"
    elif lasik and age < 40 and se <= -10:
        return "LASIK / Phakic IOL"
    elif lasik and age >= 40 and se <= -10:
        return "LASIK / Pseudophakic IOL"
    elif prk and age < 40 and se <= -10:
        return "PRK / Phakic IOL"
    elif prk and age >= 40 and se <= -10:
        return "PRK / Pseudophakic IOL"
    elif lasik:
        return "LASIK"
    elif prk:
        return "PRK"
    elif phakic:
        return "Phakic IOL"
    elif pseudophakic:
        return "Pseudophakic IOL"
    else:
        return "No suitable surgery recommended"


def check_warnings(k_avg_pre, pachy_pre, pachy_post, se, bcva_post):
    """
    Warn about:
    - K > 49 D with pachy < 500 µm → keratoconus risk
    - Post-op pachy < 410 → ectasia risk
    - SE > -12 D → extreme myopia
    - SE > +6 D → extreme hyperopia
    - BCVA < 0.5 → poor vision
    """
    warnings = []

    if k_avg_pre > 49 and pachy_pre < 500:
        warnings.append("⚠️ Possible keratoconus risk (K > 49 D, pachy < 500 µm)")
    if pachy_post < 410:
        warnings.append("⚠️ Post-op pachymetry below 410 µm (ectasia risk)")
    if se < -12:
        warnings.append("⚠️ Extreme myopia (SE < -12 D)")
    if se > 6:
        warnings.append("⚠️ Extreme hyperopia (SE > +6 D)")
    if bcva_post < 0.5:
        warnings.append("⚠️ Poor BCVA (< 0.5)")

    return warnings
