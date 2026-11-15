from app.domain.validators import validate_all

def test_r001_allergy():
    visit={"id":1}
    intake={"allergies":"penicillin","meds":"penicillin"}
    res = validate_all(visit, intake, [])
    assert any(r["rule_id"]=="R001" for r in res)

def test_r002_dose_high():
    visit={}
    intake={"dose_mg":800,"weight_kg":50}
    res = validate_all(visit, intake, [])
    assert any(r["rule_id"]=="R002" and r["severity"]=="error" for r in res)

def test_r003_interaction():
    visit={}
    intake={"meds":"warfarin, aspirin"}
    res = validate_all(visit, intake, [])
    assert any(r["rule_id"]=="R003" for r in res)

def test_r005_consent():
    visit={"consent":False}
    intake={}
    res = validate_all(visit, intake, [{"kind":"image"}])
    assert any(r["rule_id"]=="R005" for r in res)

def test_r006_low_confidence():
    visit={"transcript_confidence":0.4}
    res = validate_all(visit, {}, [])
    assert any(r["rule_id"]=="R006" for r in res)

def test_r008_missing_vitals():
    visit={}
    intake={"weight_kg":70}
    res = validate_all(visit, intake, [])
    assert any(r["rule_id"]=="R008" for r in res)
