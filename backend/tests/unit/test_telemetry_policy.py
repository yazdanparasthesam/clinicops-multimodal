from app.infra.telemetry.logging import WHITELIST
def test_no_pii_in_whitelist():
    for forbidden in ["patient_name","national_id","image_bytes","email"]:
        assert forbidden not in WHITELIST

def test_required_fields_present():
    assert "trace_id" in WHITELIST
    assert "method" in WHITELIST
