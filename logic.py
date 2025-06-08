def calculate_ablation_depth(sphere: float, cylinder: float) -> float:
    # Ablation depth formula:
    # Myopia: 15 * (|sphere| + |cylinder|)
    # Hyperopia: 1 * (|sphere| + |cylinder|)
    if sphere <= 0:  # myopia or zero
        return 15 * (abs(sphere) + abs(cylinder))
    else:  # hyperopia
        return 1 * (abs(sphere) + abs(cylinder))

def calculate_postop_k(K1_pre: float, K2_pre: float, sphere: float, cylinder: float) -> tuple:
    abs_sphere = abs(sphere)
    abs_cyl = abs(cylinder)
    if sphere <= 0:  # myopia
        delta_K1 = abs_sphere * 0.8
        delta_K2 = (abs_sphere + abs_cyl) * 0.8
        K1_post = K1_pre - delta_K1
        K2_post = K2_pre - delta_K2
    else:  # hyperopia
        delta_K1 = abs_sphere * 1.2
        delta_K2 = (abs_sphere + abs_cyl) * 1.2
        K1_post = K1_pre + delta_K1
        K2_post = K2_pre + delta_K2
    return round(K1_post, 2), round(K2_post, 2)

def calculate_postop_pachymetry(pachy_pre: float, ablation_depth: float) -> float:
    pachy_post = pachy_pre - ablation_depth
    return round(pachy_post, 2)

def calculate_postop_bcva(bcva_pre: float, sphere: float) -> float:
    # BCVA improvement formula considering minification elimination
    # bcva_post = bcva_pre * (1 + (|SE| / 10)), capped at 1.5
    bcva_post = bcva_pre * (1 + (abs(sphere) / 10))
    return round(min(bcva_post, 1.5), 2)

def determine_surgery(sphere: float, cylinder: float, pachy_pre: float, pachy_post: float, k_avg_post: float, age: int) -> str:
    SE = sphere + cylinder
    # Surgery decision logic
    if pachy_pre >= 500 and pachy_post >= 410 and 36 <= k_avg_post <= 49:
        return "LASIK"
    elif SE < 0 and 460 <= pachy_pre < 500 and pachy_post >= 410 and 36 <= k_avg_post <= 49:
        return "PRK"
    else:
        return "Phakic IOL"

def check_warnings(k_avg_pre: float, pachy_pre: float, pachy_post: float, sphere: float, bcva_post: float) -> list:
    warnings = []
    if k_avg_pre > 49 and pachy_pre < 500:
        warnings.append("Keratoconus Risk")
    if pachy_post < 410:
        warnings.append("Ectasia Risk")
    if sphere + 0 > 6:  # flag extreme hyperopia if SE > +6
        warnings.append("Extreme Hyperopia")
    if bcva_post < 0.5:
        warnings.append("Poor Vision")
    return warnings
