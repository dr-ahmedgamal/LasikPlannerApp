def calculate_postop_k(k1_pre, k2_pre, sphere, cylinder):
    k_change = 0.2 * (abs(sphere) + abs(cylinder))
    if sphere <= 0:
        return k1_pre - k_change, k2_pre - k_change
    else:
        return k1_pre + k_change, k2_pre + k_change

def calculate_postop_pachymetry(pachy_pre, ablation_depth):
    return pachy_pre - ablation_depth

def calculate_postop_bcva(bcva_pre, sphere):
    # Minification effect in myopia: improvement proportional to correction
    if sphere < 0:
        improvement = 0.05 * abs(sphere)  # adjustable coefficient
    else:
        improvement = 0
    bcva_post = bcva_pre + improvement
    return min(bcva_post, 1.5)

def determine_surgery(sphere, cylinder, pachy_pre, pachy_post, k_avg_post, age):
    if (
        sphere <= 0 and
        pachy_pre >= 500 and
        pachy_post >= 410 and
        36 <= k_avg_post <= 49
    ):
        return "LASIK"
    elif (
        sphere < 0 and
        460 <= pachy_pre < 500 and
        pachy_post >= 410 and
        36 <= k_avg_post <= 49
    ):
        return "PRK"
    else:
        return "Phakic IOL"

def check_warnings(k_avg_pre, pachy_pre, pachy_post, sphere, bcva_post):
    warnings = []
    if pachy_post < 410:
        warnings.append("Post-op pachymetry too low")
    if k_avg_pre < 36 or k_avg_pre > 49:
        warnings.append("Pre-op Kavg out of safe range")
    if bcva_post < 0.3:
        warnings.append("Post-op BCVA may be unsatisfactory")
    if abs(sphere) > 10:
        warnings.append("High refractive error — consider special assessment")
    return warnings
