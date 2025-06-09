
def calculate_postop_k(k1_pre, k2_pre, sphere, cylinder): 
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
    abs_sphere = abs(sphere)
    abs_cylinder = abs(cylinder)
    ablation_depth = 1.1 * ((optical_zone ** 2) / 3) * (abs_sphere + abs_cylinder)
    return round(ablation_depth, 2)


def calculate_postop_pachymetry(pachy_pre, sphere, cylinder, optical_zone):
    ablation_depth = calculate_ablation_depth(sphere, cylinder, optical_zone)
    if sphere < 0:  # Myopia
        pachy_post = pachy_pre - ablation_depth
    else:  # Hyperopia
        pachy_post = pachy_pre - 6  # Fixed small decrease

    return round(pachy_post, 2), ablation_depth


def calculate_postop_bcva(bcva_pre, sphere):
    abs_sphere = abs(sphere)
    bcva_post = bcva_pre + (abs_sphere * 0.05)
    return round(min(bcva_post, 1.5), 2)


def determine_surgery(sphere, cylinder, pachy_pre, pachy_post, k_avg_post, age, max_ablation_depth):
    se = sphere + (cylinder / 2)
    abs_cylinder = abs(cylinder)

    lasik_eligible = (
        pachy_pre >= 500 and
        pachy_post >= 410 and
        36 <= k_avg_post <= 49 and
        max_ablation_depth <= 140
    )

    prk_eligible = (
        se < 0 and
        pachy_pre >= 460 and
        pachy_post >= 400 and
        36 <= k_avg_post <= 49 and
        max_ablation_depth <= 90
    )

    iol_eligible = se <= -10 or se >= +7
    phakic_eligible = iol_eligible and age < 40
    pseudophakic_eligible = iol_eligible and age >= 40

    if lasik_eligible and prk_eligible:
        return "LASIK / PRK"
    elif lasik_eligible and phakic_eligible:
        return "LASIK / Phakic IOL"
    elif lasik_eligible and pseudophakic_eligible:
        return "LASIK / Pseudophakic IOL"
    elif lasik_eligible:
        return "LASIK"
    elif prk_eligible and phakic_eligible:
        return "PRK / Phakic IOL"
    elif prk_eligible and pseudophakic_eligible:
        return "PRK / Pseudophakic IOL"
    elif prk_eligible:
        return "PRK"
    elif phakic_eligible:
        return "Phakic IOL"
    elif pseudophakic_eligible:
        return "Pseudophakic IOL"
    else:
        return "No suitable surgery recommended"


def check_warnings(k_avg_pre, pachy_pre, pachy_post, sphere, bcva_post, cylinder=0, k_avg_post=None):
    se = sphere + (cylinder / 2)
    warnings = []

    if k_avg_pre > 49 and pachy_pre < 500:
        warnings.append("Keratoconus risk: K > 49 D with pachy < 500 µm")
    if pachy_post < 410:
        warnings.append("Ectasia risk: post-op pachy < 410 µm")
    if se < -12:
        warnings.append("Extreme myopia (SE < -12 D)")
    if se > 6:
        warnings.append("Extreme hyperopia (SE > +6 D)")
    if bcva_post < 0.5:
        warnings.append("Poor BCVA: post-op BCVA < 0.5")
    if not (36 <= k_avg_pre <= 49):
        warnings.append("Pre-op K average out of range (36–49 D)")
    if k_avg_post is not None and not (36 <= k_avg_post <= 49):
        warnings.append("Post-op K average out of range (36–49 D)")

    return warnings
