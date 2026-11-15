import pytest
from app.domain.scores import bmi, map_score, bsa, egfr, compute_all, dose_per_kg, adherence

def test_bmi():
    assert bmi(70, 175) == 22.9
    with pytest.raises(ValueError):
        bmi(None, 175)

def test_map():
    assert map_score(120,80) == 93.3

def test_bsa():
    v = bsa(70,175)
    assert 1.8 < v < 1.9

def test_egfr_female():
    v = egfr(0.9, 40, "female")
    assert 70 < v < 150

def test_compute_all():
    intake = {"weight_kg":70,"height_cm":175,"systolic":120,"diastolic":80,"creatinine":1.0,"age":40,"sex":"male","dose_mg":100,"taken":28,"prescribed":30,"dvt_factors":{"active_cancer":True},"conditions":["htn"],"weight_kg":70}
    out = compute_all(intake)
    assert out["bmi"] == 22.9
    assert out["map"] == 93.3
    assert out["wells"] == 1
    assert out["adherence"] == 93.3

def test_dose_per_kg():
    assert dose_per_kg(100,50) == 2.0

def test_adherence():
    assert adherence(28,30) == 93.3
