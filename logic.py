def calculate_postop_k(k1_pre, k2_pre, sphere, cylinder):
    """
    Calculate post-op K1 and K2 using your latest formulas.

    Myopia:
        ΔK1 = |Sphere| × 0.8
        ΔK2 = (|Sphere| + |Cylinder|) × 0.8
        Post-op = Pre-op - ΔK

    Hyperopia:
        ΔK1 = |Sphere| × 1.2
        ΔK2 = (|Sphere| - |Cylinder|) × 1.2  # Use difference, not sum
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
    Ablation Depth using Munnerlyn formula with 1.1 correction factor:
    Ablation Depth = 1.1 × (Optical Zone^2 / 3) × (|Sphere| + |Cylinder|)
    """
    abs_sphere = abs(sphere)
    abs_cylinder = abs(cylinder)
    ablation_depth = 1.1 * ((optical_zone ** 2) / 3) * (abs_sphere + abs_cylinder)
    return round(ablation_depth, 2)


def calculate_postop_pachymetry(pachy_pre, sphere, cylinder, optical_zone):
    """
    Post-op pachymetry calculation:
    - Myopia: Subtract ablation depth from pre-op pachy
    - Hyperopia: Subtract fixed 6 µm from pre-op pachy (not ablation depth)
    """
    ablation_depth = calculate_ablation_depth(sphere, cylinder, optical_zone)
    if sphere < 0:  # Myopia
        pachy_post = pachy_pre - ablation_depth
    else:  # Hyperopia
        pachy_post = pachy_pre - 6  # Fixed small decrease

    return round(pachy_post, 2), ablation_depth


def calculate_postop_bcva(bcva_pre, sphere):
    """
    Post-op BCVA approximation:
    BCVA_post = min(BCVA_pre + (|SE| × 0.05), 1.5)
    """
    abs_sphere = abs(sphere)
    bcva_post = bcva_pre + (abs_sphere * 0.05)
    return round(min(bcva_post, 1.5), 2)


def determine_surgery(sphere, cylinder, pachy_pre, pachy_post, k_avg_post, age, max_ablation_depth):
    """
    Determine recommended surgery based on updated criteria:

    LASIK:
      - Pre-op pachy ≥ 500 µm
      - Post-op pachy ≥ 410 µm
      - SE between -12 and +7 D
      - Post-op K_avg between 36 and 49 D
      - Cylinder ≤ 6 D
      - Max ablation depth ≤ 140 µm

    PRK:
      - Sphere < 0 (myopia only)
      - Pre-op pachy > 460 µm
      - Post-op pachy ≥ 400 µm
      - Post-op K_avg between 36 and 49 D
      - Cylinder ≤ 6 D
      - Max ablation depth ≤ 90 µm

    Phakic IOL:
      - SE ≤ -8 D or SE ≥ +7 D
      - Age < 40

    Pseudophakic IOL:
      - Same SE as Phakic IOL
      - Age ≥ 40

    If both LASIK and PRK eligible, recommend "LASIK / PRK" (LASIK first)
    """
    se = sphere + (cylinder / 2)
    abs_cylinder = abs(cylinder)

    lasik_eligible = (
        pachy_pre >= 500
        and pachy_post >= 410
        and (-12 <= se <= 7)
        and (36 <= k_avg_post <= 49)
        and abs_cylinder <= 6
        and max_ablation_depth <= 140
    )

    prk_eligible = (
        sphere < 0
        and pachy_pre > 460
        and pachy_post >= 400
        and (36 <= k_avg_post <= 49)
        and abs_cylinder <= 6
        and max_ablation_depth <= 90
    )

    phakic_iol_eligible = (se <= -8 or se >= 7) and age < 40
    pseudophakic_iol_eligible = (se <= -8 or se >= 7) and age >= 40

    options = []
    if lasik_eligible:
        options.append("LASIK")
    if prk_eligible:
        options.append("PRK")
    if phakic_iol_eligible:
        options.append("Phakic IOL")
    if pseudophakic_iol_eligible:
        options.append("Pseudophakic IOL")

    if "LASIK" in options and "PRK" in options:
        return "LASIK / PRK"
    elif options:
        return " / ".join(options)
    else:
        return "No suitable surgery recommended"


def check_warnings(k_avg_pre, pachy_pre, pachy_post, sphere, bcva_post, cylinder=0, k_avg_post=None):
    """
    Warning flags based on latest thresholds:

    - Thin cornea pre-op: pachy < 480 µm
    - Thin cornea post-op: pachy < 400 µm
    - Extreme cylinder: cylinder < -6 D (negative values)
    - BCVA decrease potential: post-op BCVA < 1.0
    - Pre-op K average out of range (36–49 D)
    - Post-op K average out of range (36–49 D)
    """
    warnings = []

    if pachy_pre < 480:
        warnings.append("Warning: Thin cornea pre-op (<480 µm)")
    if pachy_post < 400:
        warnings.append("Warning: Thin cornea post-op (<400 µm)")
    if cylinder < -6:
        warnings.append("Warning: Extreme cylinder (>6 D)")
    if bcva_post < 1.0:
        warnings.append("Warning: Potential BCVA decrease")
    if not (36 <= k_avg_pre <= 49):
        warnings.append("Warning: Pre-op K average out of range (36–49 D)")
    if k_avg_post is not None and not (36 <= k_avg_post <= 49):
        warnings.append("Warning: Post-op K average out of range (36–49 D)")

    return warnings
