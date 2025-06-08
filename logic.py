def calculate_postop_k(k1_pre, k2_pre, sphere, cylinder):
    # ΔK1 and ΔK2 formulas depend on myopia/hyperopia and cylinder addition
    abs_sphere = abs(sphere)
    abs_cyl = abs(cylinder)

    if sphere <= 0:  # Myopia
        delta_k1 = abs_sphere * 0.8
        delta_k2 = (abs_sphere + abs_cyl) * 0.8
        k1_post = k1_pre - delta_k1
        k2_post = k2_pre - delta_k2
    else:  # Hyperopia
        delta_k1 = abs_sphere * 1.2
        delta_k2 = (abs_sphere + abs_cyl) * 1.2
        k1_post = k1_pre + delta_k1
        k2_post = k2_pre + delta_k2

    return k1_post, k2_post


def calculate_postop_pachymetry(pachy_pre, ablation_depth):
    pachy_post = pachy_pre - ablation_depth
    return pachy_post


def calculate_postop_bcva(bcva_pre, sphere):
    # BCVA improves linearly based on minification elimination in myopia
    # Formula: BCVApost = BCVApre + 0.1 * |SE| capped at max 1.5
    bcva_post = bcva_pre + 0.1 * abs(sphere)
    if bcva_post > 1.5:
        bcva_post = 1.5
    return bcva_post


def determine_surgery(sphere, cylinder, pachy_pre, pachy_post, k_avg_post, age):
    abs_sphere = abs(sphere)
    abs_cyl = abs(cylinder)
    se = sphere + cylinder  # Spherical equivalent (approximate)

    # Final SE for surgery logic uses Sphere + Cylinder (absolute)
    se_total = abs_sphere + abs_cyl

    # LASIK criteria
    if (
        pachy_pre >= 500
        and pachy_post >= 410
        and 36 <= k_avg_post <= 49
        and ((sphere <= 0 and ablation_depth_myopia := 15 * se_total) <= 140
             or (sphere > 0 and ablation_depth_hyperopia := 1 * se_total) <= 140)
    ):
        return "LASIK"

    # PRK criteria
    if (
        sphere < 0  # Only myopia or astigmatism (no hyperopia)
        and pachy_pre >= 460
        and pachy_post >= 400
        and 36 <= k_avg_post <= 49
        and (15 * se_total) <= 90  # max ablation depth for PRK (myopia)
    ):
        return "PRK"

    # Phakic IOL fallback for <40 years old
    if age < 40:
        return "Phakic IOL (Fallback)"

    # Pseudo-Phakic IOL fallback for 40+ years
    if age >= 40:
        return "Pseudo-Phakic IOL (Fallback)"

    # Default fallback
    return "Not Eligible"


def check_warnings(k_avg_pre, pachy_pre, pachy_post, sphere, bcva_post):
    warnings = []

    # Keratoconus risk
    if k_avg_pre > 49 and pachy_pre < 500:
        warnings.append("Keratoconus risk")

    # Ectasia risk
    if pachy_post < 410:
        warnings.append("Ectasia risk")

    # Extreme hyperopia
    se = sphere  # For hyperopia warning we consider sphere only
    if se > 6:
        warnings.append("Extreme hyperopia")

    # Extreme myopia (added as per your note in warnings)
    if se < -12:
        warnings.append("Extreme myopia")

    # Poor vision flag
    if bcva_post < 0.5:
        warnings.append("Poor vision (BCVA < 0.5)")

    return warnings
