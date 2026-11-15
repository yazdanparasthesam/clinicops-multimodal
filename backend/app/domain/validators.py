from typing import List, Dict

# R001-R008 validators - pure functions

def r001_allergy(visit: dict, intake: dict) -> dict | None:
    allergies = (intake.get("allergies") or "").lower()
    meds = (intake.get("meds") or "").lower()
    if allergies and meds and allergies in meds:
        return {"rule_id":"R001","severity":"error","message":f"Drug-allergy conflict: patient allergic to {allergies} but prescribed {meds}","field":"allergies"}
    return None

def r002_dose_range(intake: dict) -> dict | None:
    dose = intake.get("dose_mg")
    weight = intake.get("weight_kg")
    if dose and weight:
        dpk = dose/weight
        if dpk > 10:  # >10 mg/kg
            return {"rule_id":"R002","severity":"error","message":f"Dose {dpk:.1f} mg/kg exceeds max 10 mg/kg","field":"dose_mg"}
        if dpk < 0.1:
            return {"rule_id":"R002","severity":"warn","message":f"Dose very low {dpk:.2f} mg/kg","field":"dose_mg"}
    return None

def r003_interaction(intake: dict) -> dict | None:
    meds = intake.get("meds","").lower()
    if "warfarin" in meds and "aspirin" in meds:
        return {"rule_id":"R003","severity":"error","message":"Warfarin + Aspirin major interaction (bleeding risk)","field":"meds"}
    return None

def r004_duplicate(intake: dict) -> dict | None:
    meds = intake.get("meds","").lower().split(",")
    meds = [m.strip() for m in meds if m.strip()]
    if len(meds) != len(set(meds)):
        return {"rule_id":"R004","severity":"warn","message":"Duplicate therapy detected","field":"meds"}
    return None

def r005_consent(visit: dict, attachments: List[Dict]) -> dict | None:
    has_image = any(a.get("kind")=="image" for a in attachments)
    consent = visit.get("consent") or intake_consent_fallback(visit)
    if has_image and not consent:
        return {"rule_id":"R005","severity":"error","message":"Image attachment without consent flag","field":"consent"}
    return None

def intake_consent_fallback(visit: dict):
    return visit.get("allergies_consent") or False

def r006_transcript_confidence(visit: dict) -> dict | None:
    conf = visit.get("transcript_confidence")
    if conf is not None and conf < 0.6:
        return {"rule_id":"R006","severity":"warn","message":f"Transcript confidence {conf:.2f} < 0.6 — verify manually","field":"transcript"}
    return None

def r007_vitals_range(intake: dict) -> dict | None:
    s = intake.get("systolic")
    if s is not None and (s < 70 or s > 250):
        return {"rule_id":"R007","severity":"warn","message":f"Systolic {s} out of physiological range","field":"systolic"}
    h = intake.get("weight_kg")
    if h is not None and (h < 1 or h > 300):
        return {"rule_id":"R007","severity":"warn","message":f"Weight {h} out of range","field":"weight_kg"}
    return None

def r008_missing_vitals(intake: dict) -> dict | None:
    required = ["weight_kg","height_cm","systolic","diastolic"]
    missing = [k for k in required if intake.get(k) is None]
    if missing:
        return {"rule_id":"R008","severity":"error","message":f"Missing required vitals: {', '.join(missing)}","field":"vitals"}
    return None

def validate_all(visit: dict, intake: dict, attachments: List[Dict]) -> List[Dict]:
    checks = [
        r001_allergy(visit, intake),
        r002_dose_range(intake),
        r003_interaction(intake),
        r004_duplicate(intake),
        r005_consent(visit, attachments),
        r006_transcript_confidence(visit),
        r007_vitals_range(intake),
        r008_missing_vitals(intake),
    ]
    return [c for c in checks if c]
