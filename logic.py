
from utils.helpers import calculate_ablation_depth, calculate_delta_k1, calculate_delta_k2

def is_myopia(se):
    return se <= 0

def calculate_postop_k(K1_pre, K2_pre, sphere, cylinder):
    myopia = is_myopia(sphere)
    delta_k1 = calculate_delta_k1(sphere, myopia)
    delta_k2 = calculate_delta_k2(sphere, cylinder, myopia)

    if myopia:
        K1_post = K1_pre - delta_k1
        K2_post = K2_pre - delta_k2
    else:
        K1_post = K1_pre + delta_k1
        K2_post = K2_pre + delta_k2

    return K1_post, K2_post

def calculate_postop_pachymetry(pachymetry_pre, ablation_depth):
    return pachymetry_pre - ablation_depth

def calculate_postop_bcva(bcva_pre, se):
    # Correcting minification effect in myopia, capped at 1.5
    improvement = 0.1 * abs(se)
    bcva_post = min(bcva_pre + improvement, 1.5)
    return bcva_post

def determine_surgery(sphere, cylinder, pachy_pre, pachy_post, k_avg_post, age):
    se = sphere
    if (pachy_pre >= 500 and pachy_post >= 410 and 36 <= k_avg_post <= 49 and abs(se) <= 12):
        return "LASIK"
    if (se < 0 and pachy_pre >= 460 and pachy_post >= 400 and 36 <= k_avg_post <= 49 and abs(se) <= 12):
        return "PRK"
    if age < 40:
        return "Phakic IOL (fallback)"
    else:
        return "Pseudo-Phakic IOL (fallback)"

def check_warnings(k_avg_pre, pachy_pre, pachy_post, se, bcva_post):
    warnings = []
    if k_avg_pre > 49 and pachy_pre < 500:
        warnings.append("Keratoconus risk")
    if pachy_post < 410:
        warnings.append("Ectasia risk")
    if se > 6:
        warnings.append("Extreme hyperopia")
    if se < -12:
        warnings.append("Extreme myopia")
    if bcva_post < 0.5:
        warnings.append("Poor vision")
    return warnings
