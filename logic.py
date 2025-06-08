# logic.py

def calculate_postop_k(K1_pre, K2_pre, sphere, cylinder):
    if sphere <= 0:  # Myopia
        delta_k1 = 0.5 * abs(sphere)
        delta_k2 = 0.5 * abs(sphere + cylinder)
        K1_post = K1_pre - delta_k1
        K2_post = K2_pre - delta_k2
    else:  # Hyperopia
        delta_k1 = 0.5 * abs(sphere)
        delta_k2 = 0.5 * abs(sphere + cylinder)
        K1_post = K1_pre + delta_k1
        K2_post = K2_pre + delta_k2

    return K1_post, K2_post


def calculate_postop_pachymetry(pachy_pre, ablation_depth):
    return pachy_pre - ablation_depth


def calculate_postop_bcva(bcva_pre, sphere):
    improvement = 0.02 * abs(sphere) if sphere < 0 else 0
    bcva_post = bcva_pre + improvement
    return min(round(bcva_post, 2), 1.5)


def determine_surgery(sphere, cylinder, pachy_pre, pachy_post, k_avg_post, age):
    abs_sphere = abs(sphere)
    abs_cyl = abs(cylinder)
    se = sphere + cylinder  # Spherical equivalent
    se_total = abs_sphere + abs_cyl

    if sphere <= 0:
        ablation_depth = 15 * se_total
    else:
        ablation_depth = 1 * se_total

    if (
        pachy_pre >= 500 and
        pachy_post >= 410 and
        36 <= k_avg_post <= 49 and
        ablation_depth <= 140
    ):
        return "LASIK"

    if (
        sphere < 0 and
        pachy_pre >= 460 and
        pachy_post >= 400 and
        36 <= k_avg_post <= 49 and
        (15 * se_total) <= 90
    ):
        return "PRK"

    if age < 40:
        return "Phakic IOL (Fallback)"

    if age >= 40:
        return "Pseudo-Phakic IOL (Fallback)"

    return "Not Eligible"


def check_warnings(k_avg_pre, pachy_pre, pachy_post, sphere, bcva_post):
    warnings = []
    if k_avg_pre > 49 and pachy_pre < 500:
        warnings.append("⚠ Keratoconus risk")
    if pachy_post < 410:
        warnings.append("⚠ Ectasia risk")
    if sphere > 6:
        warnings.append("⚠ Extreme hyperopia")
    if sphere < -12:
        warnings.append("⚠ Extreme myopia")
    if bcva_post < 0.5:
        warnings.append("⚠ Poor vision")
    return warnings
