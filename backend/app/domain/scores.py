import math

def bmi(weight_kg: float, height_cm: float) -> float:
    if not weight_kg or not height_cm:
        raise ValueError("missing")
    h_m = height_cm / 100.0
    return round(weight_kg / (h_m * h_m), 1)

def map_score(systolic: float, diastolic: float) -> float:
    if not systolic or not diastolic:
        raise ValueError("missing")
    return round((systolic + 2 * diastolic) / 3, 1)

def bsa(weight_kg: float, height_cm: float) -> float:
    # Mosteller
    if not weight_kg or not height_cm:
        raise ValueError("missing")
    return round(math.sqrt(weight_kg * height_cm / 3600), 2)

def egfr(creatinine_mgdl: float, age: int, sex: str) -> float:
    # Simplified CKD-EPI 2021 without race
    if not creatinine_mgdl or not age:
        raise ValueError("missing")
    k = 0.7 if sex == "female" else 0.9
    a = -0.241 if sex == "female" else -0.302
    scr_k = creatinine_mgdl / k
    min_term = min(scr_k, 1) ** a
    max_term = max(scr_k, 1) ** -1.200
    egfr_val = 142 * min_term * max_term * (0.9938 ** age) * (1.012 if sex == "female" else 1)
    return round(egfr_val, 0)

def cci(age: int, conditions: list) -> int:
    # Simplified charlson: age points + condition count
    age_pts = 0
    if age >= 50: age_pts = (age - 40) // 10
    return age_pts + len(conditions)

def wells_score(dvt_factors: dict) -> int:
    # Simplified Wells DVT: sum of booleans
    score = 0
    for k, v in dvt_factors.items():
        if v:
            score += 1
    return score

def dose_per_kg(dose_mg: float, weight_kg: float) -> float:
    if not dose_mg or not weight_kg:
        raise ValueError("missing")
    return round(dose_mg / weight_kg, 2)

def adherence(taken: int, prescribed: int) -> float:
    if prescribed == 0:
        return 0.0
    return round(taken / prescribed * 100, 1)

def apgar(scores: dict) -> int:
    # scores: appearance, pulse, grimace, activity, respiration each 0-2
    return sum(scores.values())

def risk_score(bmi_val: float, egfr_val: float, wells: int) -> float:
    # Composite demo: weighted
    if bmi_val is None or egfr_val is None:
        return 0.0
    return round((bmi_val * 0.5) + ((100 - egfr_val) * 0.3) + (wells * 5), 1)

def compute_all(intake: dict) -> dict:
    """Pure function: compute all scores from intake dict, never raises unhandled."""
    out = {}
    try:
        out["bmi"] = bmi(intake.get("weight_kg"), intake.get("height_cm"))
    except Exception:
        out["bmi"] = None
    try:
        out["map"] = map_score(intake.get("systolic"), intake.get("diastolic"))
    except Exception:
        out["map"] = None
    try:
        out["bsa"] = bsa(intake.get("weight_kg"), intake.get("height_cm"))
    except Exception:
        out["bsa"] = None
    try:
        out["egfr"] = egfr(intake.get("creatinine"), intake.get("age"), intake.get("sex", "male"))
    except Exception:
        out["egfr"] = None
    out["cci"] = cci(intake.get("age", 0), intake.get("conditions", []))
    out["wells"] = wells_score(intake.get("dvt_factors", {}))
    try:
        out["dose_per_kg"] = dose_per_kg(intake.get("dose_mg"), intake.get("weight_kg"))
    except Exception:
        out["dose_per_kg"] = None
    out["adherence"] = adherence(intake.get("taken", 0), intake.get("prescribed", 0))
    try:
        out["apgar"] = apgar(intake.get("apgar_scores", {"a":0,"p":0,"g":0,"ac":0,"r":0}))
    except Exception:
        out["apgar"] = 0
    out["risk"] = risk_score(out.get("bmi"), out.get("egfr"), out.get("wells"))
    out["bmi_z"] = round((out["bmi"] - 22) / 5, 2) if out.get("bmi") else None
    return out
