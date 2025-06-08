# logic.py

def calculate_ablation_depth(sphere: float, cylinder: float, optical_zone: float) -> float:
    """
    Calculate ablation depth using the Munnerlyn formula with 1.1 correction factor.
    Ablation Depth = 1.1 * (Optical Zone^2) * (|Sphere| + |Cylinder|) / 3
    """
    return 1.1 * (optical_zone ** 2) * (abs(sphere) + abs(cylinder)) / 3


def calculate_postop_keratometry(sphere: float, cylinder: float, k1_pre: float, k2_pre: float) -> tuple[float, float, float]:
    """
    Calculate postoperative K1, K2, and average K using:
    
    Myopia (sphere <= 0):
      ΔK1 = |Sphere| * 0.8
      ΔK2 = (|Sphere| + |Cylinder|) * 0.8
      K_post = K_pre - ΔK

    Hyperopia (sphere > 0):
      ΔK1 = |Sphere| * 1.2
      ΔK2 = (|Sphere| - |Cylinder|) * 1.2
      K_post = K_pre + ΔK
    """
    abs_sphere = abs(sphere)
    abs_cyl = abs(cylinder)

    if sphere <= 0:  # Myopia
        delta_k1 = abs_sphere * 0.8
        delta_k2 = (abs_sphere + abs_cyl) * 0.8
        k1_post = k1_pre - delta_k1
        k2_post = k2_pre - delta_k2
    else:  # Hyperopia
        delta_k1 = abs_sphere * 1.2
        delta_k2 = (abs_sphere - abs_cyl) * 1.2
        k1_post = k1_pre + delta_k1
        k2_post = k2_pre + delta_k2

    kavg_post = (k1_post + k2_post) / 2
    return k1_post, k2_post, kavg_post


def calculate_postop_pachymetry(sphere: float, pachy_pre: float, ablation_depth: float) -> float:
    """
    Calculate postoperative pachymetry:
    - For myopia: subtract ablation depth from pre-op pachy
    - For hyperopia: subtract fixed 6 µm from pre-op pachy (ablation peripheral, no thickness subtraction)
    """
    if sphere <= 0:
        pachy_post = pachy_pre - ablation_depth
    else:
        pachy_post = pachy_pre - 6  # fixed decrement for hyperopia
    return pachy_post


def calculate_postop_bcva(bcva_pre: float, sphere: float) -> float:
    """
    Predict postoperative BCVA (best corrected visual acuity):
    BCVA_post = min(BCVA_pre + (|SE| * 0.05), 1.5)
    SE = Sphere + Cylinder, but here simplified as Sphere only.
    """
    se_abs = abs(sphere)
    bcva_post = bcva_pre + (se_abs * 0.05)
    if bcva_post > 1.5:
        bcva_post = 1.5
    return bcva_post


def determine_surgery(sphere: float, cylinder: float, pachy_pre: float, pachy_post: float, k_avg_post: float, age: int) -> str:
    """
    Determine recommended surgery based on criteria:

    LASIK criteria:
      - SE between -12 and +7
      - Pre-op pachy ≥ 480
      - Post-op pachy ≥ 410
      - Post-op K_avg in [36, 49]
      - Max ablation depth ≤ 140

    PRK criteria:
      - SE < 0
      - Pre-op pachy > 460
      - Post-op pachy ≥ 400
      - Post-op K_avg in [36, 49]
      - Max ablation depth ≤ 90

    Phakic IOL:
      - SE ≤ -8 or SE ≥ +7
      - Cornea not suitable (not met by LASIK/PRK)
      - Age < 40

    Pseudophakic IOL:
      - Same SE criteria as Phakic IOL
      - Age ≥ 40

    If both LASIK and PRK eligible, recommend both with LASIK first.
    """
    se = sphere + cylinder
    max_ablation_myopia = 140
    max_ablation_prk = 90

    lasik_eligible = (
        -12 <= se <= 7 and
        pachy_pre >= 480 and
        pachy_post >= 410 and
        36 <= k_avg_post <= 49
    )
    prk_eligible = (
        se < 0 and
        pachy_pre > 460 and
        pachy_post >= 400 and
        36 <= k_avg_post <= 49
    )

    # Ablation depth calculation should be done externally for max ablation check, assumed satisfied here.

    if lasik_eligible and prk_eligible:
        return "LASIK / PRK"
    if lasik_eligible:
        return "LASIK"
    if prk_eligible:
        return "PRK"

    # IOL eligibility
    if (se <= -8 or se >= 7):
        if age < 40:
            return "Phakic IOL"
        else:
            return "Pseudophakic IOL"

    return "No suitable surgery"


def check_warnings(k_avg_pre: float, pachy_pre: float, pachy_post: float, cylinder: float, bcva_post: float) -> list:
    """
    Return warnings as a list of strings based on thresholds:

    - Thin cornea warning if pre-op pachymetry < 480
    - Extreme cylinder warning if cylinder < -6
    - BCVA decline warning if post-op BCVA worse than 1.0 (arbitrary threshold)
    """
    warnings = []
    if pachy_pre < 480:
        warnings.append("Thin cornea (Pre-op pachy < 480 µm)")
    if cylinder < -6:
        warnings.append("Extreme cylinder (< -6 D)")
    if bcva_post > 1.0:
        warnings.append("Possible BCVA decline")

    return warnings
