def calculate_postop_k(k1_pre, k2_pre, sphere, cylinder):
    k1_post = round(k1_pre - sphere, 2)
    k2_post = round(k2_pre - (sphere + cylinder), 2)
    return k1_post, k2_post


def calculate_ablation_depth(sphere, cylinder, optical_zone):
    se = sphere + (cylinder / 2)
    ablation = abs(se) * (optical_zone ** 2) / 3
    ablation *= 1.1  # Apply Munnerlyn correction factor
    return round(ablation, 2)


def calculate_postop_pachymetry(pachy_pre, sphere, cylinder, optical_zone):
    ablation_depth = calculate_ablation_depth(sphere, cylinder, optical_zone)

    if sphere >= 0:
        # For hyperopia, post-op pachy is pre-op minus fixed 6 µm
        pachy_post = pachy_pre - 6
    else:
        # For myopia/astigmatism, subtract ablation depth
        pachy_post = pachy_pre - ablation_depth

    return round(pachy_post, 2), ablation_depth


def calculate_postop_bcva(bcva_pre, sphere):
    se = abs(sphere)
    if se > 10:
        return round(max(bcva_pre - 0.2, 0.0), 2)
    return round(bcva_pre, 2)


def determine_surgery(sphere, cylinder, pachy_pre, pachy_post, k_avg_post, age):
    se = sphere + (cylinder / 2)
    ablation_depth = calculate_ablation_depth(sphere, cylinder, 6.5)  # using default 6.5 mm for decision

    # LASIK eligibility criteria
    lasik_eligible = (
        pachy_pre >= 500 and
        pachy_post >= 410 and
        36 <= k_avg_post <= 49 and
        ablation_depth <= 140
    )

    # PRK eligibility criteria
    prk_eligible = (
        se < 0 and
        pachy_pre > 460 and
        pachy_post >= 400 and
        36 <= k_avg_post <= 49 and
        ablation_depth <= 90
    )

    # Phakic or Pseudophakic IOL eligibility
    iol_eligible = (
        se <= -8 or se >= +7 or
        not lasik_eligible and not prk_eligible
    )

    if iol_eligible:
        if age < 40:
            iol_type = "Phakic IOL"
        else:
            iol_type = "Pseudophakic IOL"
    else:
        iol_type = None

    # Decision logic
    if lasik_eligible and prk_eligible:
        return "LASIK / PRK"
    elif lasik_eligible:
        return f"LASIK" + (f" / {iol_type}" if iol_type else "")
    elif prk_eligible:
        return f"PRK" + (f" / {iol_type}" if iol_type else "")
    elif iol_type:
        return iol_type
    else:
        return "No Suitable Surgical Option"


def check_warnings(k_avg_pre, pachy_pre, pachy_post, sphere, bcva_post, cylinder):
    se = sphere + (cylinder / 2)
    warnings = []

    # Warning: suspicious cornea (thin + steep)
    if k_avg_pre > 48 and pachy_pre < 500:
        warnings.append("High risk of keratoconus: steep K and thin cornea (<500 µm)")

    # Warning: ectasia risk
    if pachy_post < 400:
        warnings.append("Risk of ectasia: post-op pachymetry < 400 µm")

    # Warning: high myopia or hyperopia
    if se < -12:
        warnings.append("Very high myopia: SE < –12 D")
    if se > 6:
        warnings.append("Very high hyperopia: SE > +6 D")

    # Warning: visual prognosis
    if bcva_post < 0.5:
        warnings.append("Low visual potential: predicted BCVA < 0.5")

    return warnings
