
# logic.py

def evaluate_eligibility(data):
    age = data.get("age")
    se = data.get("SE")
    preop_pachy = data.get("preop_pachymetry")
    postop_pachy = data.get("postop_pachymetry")
    postop_kavg = data.get("postop_kavg")
    ablation_depth = data.get("ablation_depth")
    bcva = data.get("BCVA")

    lasik_eligible = (
        preop_pachy >= 500 and
        postop_pachy >= 410 and
        34 <= postop_kavg <= 50 and
        ablation_depth <= 140 and
        se is not None
    )

    prk_eligible = (
        se < 0 and
        preop_pachy >= 460 and
        postop_pachy >= 400 and
        34 <= postop_kavg <= 50 and
        ablation_depth <= 90
    )

    phakic_eligible = (
        age < 40 and (
            se <= -10 or se > 6.0 or not (lasik_eligible or prk_eligible)
        )
    )

    pseudophakic_eligible = (
        age >= 40 and (
            se <= -10 or se > 6.0 or not (lasik_eligible or prk_eligible)
        )
    )

    # Determine recommendations
    recommendation = "No suitable surgery recommended"

    if lasik_eligible and prk_eligible:
        recommendation = "LASIK / PRK"
    elif lasik_eligible and (phakic_eligible or pseudophakic_eligible):
        if age < 40:
            recommendation = "LASIK / Phakic IOL"
        else:
            recommendation = "LASIK / Pseudophakic IOL"
    elif prk_eligible and (phakic_eligible or pseudophakic_eligible):
        if age < 40:
            recommendation = "PRK / Phakic IOL"
        else:
            recommendation = "PRK / Pseudophakic IOL"
    elif lasik_eligible:
        recommendation = "LASIK"
    elif prk_eligible:
        recommendation = "PRK"
    elif phakic_eligible:
        recommendation = "Phakic IOL"
    elif pseudophakic_eligible:
        recommendation = "Pseudophakic IOL"

    # Warnings
    warnings = []
    if postop_kavg > 48 and preop_pachy < 500:
        warnings.append("⚠️ Risk of keratoconus (Kavg > 48 D and pachymetry < 500 µm)")
    if postop_pachy < 400:
        warnings.append("⚠️ Risk of ectasia (Post-op pachymetry < 400 µm)")
    if se < -12:
        warnings.append("⚠️ High myopia (SE < –12 D)")
    if se > 6:
        warnings.append("⚠️ High hyperopia (SE > +6 D)")
    if bcva < 0.5:
        warnings.append("⚠️ Poor visual acuity (BCVA < 0.5)")

    return {
        "recommendation": recommendation,
        "lasik_eligible": lasik_eligible,
        "prk_eligible": prk_eligible,
        "phakic_eligible": phakic_eligible,
        "pseudophakic_eligible": pseudophakic_eligible,
        "warnings": warnings
    }
