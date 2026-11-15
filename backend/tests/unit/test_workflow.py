from app.domain.workflow import can_transition, gate_errors_for_transition, role_allowed

def test_transitions():
    assert can_transition("draft","submitted")
    assert not can_transition("draft","approved")
    assert can_transition("submitted","in_review")

def test_gate():
    assert gate_errors_for_transition("submitted",["R001"]) == ["R001"]
    assert gate_errors_for_transition("in_review", ["R001"]) == []

def test_roles():
    assert role_allowed("doctor","approved")
    assert not role_allowed("nurse","approved")
    assert role_allowed("pharmacist","dispensed")
