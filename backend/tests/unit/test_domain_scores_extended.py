from app.domain.scores import compute_all
def test_missing_intake():
    out = compute_all({})
    assert out["bmi"] is None
    assert out["cci"]==0

def test_bmi_z():
    out = compute_all({"weight_kg":70,"height_cm":175})
    assert "bmi_z" in out
