import pytest
pytestmark = pytest.mark.integration

def test_vision_and_transcribe(client, auth_headers):
    r = client.post("/api/visits", json={"patient_name":"AI Test"}, headers=auth_headers)
    vid = r.json()["id"]
    # need image for vision
    jpg = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9"
    client.post(f"/api/visits/{vid}/attachments", files={"file":("wound.jpg", jpg, "image/jpeg")}, headers=auth_headers)
    r2 = client.post(f"/api/visits/{vid}/ai/vision-draft", json={}, headers=auth_headers)
    assert r2.status_code==200
    assert "MOCK" in r2.json()["content"] or "erythematous" in r2.json()["content"].lower()

    r3 = client.post(f"/api/visits/{vid}/ai/transcribe", json={"transcript":"Patient reports chest pain","confidence":0.92}, headers=auth_headers)
    assert r3.status_code==200
    assert r3.json()["kind"]=="transcribe"

def test_notes_and_chat(client, auth_headers):
    r = client.post("/api/visits", json={"patient_name":"Chat Test"}, headers=auth_headers)
    vid = r.json()["id"]
    r2 = client.post(f"/api/visits/{vid}/ai/notes-draft", json={}, headers=auth_headers)
    assert r2.status_code==200
    r3 = client.post(f"/api/visits/{vid}/ai/chat", json={"query":"Show scores"}, headers=auth_headers)
    assert r3.status_code==200

def test_export(client, auth_headers):
    r = client.post("/api/visits", json={"patient_name":"Export Test"}, headers=auth_headers)
    vid = r.json()["id"]
    r2 = client.get(f"/api/visits/{vid}/export/pdf", headers=auth_headers)
    assert r2.status_code==200
    assert r2.headers["content-type"]=="application/pdf"
    r3 = client.get(f"/api/visits/{vid}/export/xlsx", headers=auth_headers)
    assert r3.status_code==200

def test_auth_rbac(client, auth_headers, doctor_headers, pharmacist_headers):
    # nurse creates
    r = client.post("/api/visits", json={"patient_name":"RBAC"}, headers=auth_headers)
    vid = r.json()["id"]
    # nurse can submit after fixing vitals
    client.patch(f"/api/visits/{vid}", json={"weight_kg":70,"height_cm":175,"systolic":120,"diastolic":80}, headers=auth_headers)
    r2 = client.post(f"/api/visits/{vid}/workflow/submit", json={}, headers=auth_headers)
    assert r2.status_code==200
    # pharmacist cannot approve (needs in_review first) - check role rejection from in_review state
    client.post(f"/api/visits/{vid}/workflow/start_review", json={}, headers=doctor_headers)
    r3 = client.post(f"/api/visits/{vid}/workflow/approve", json={}, headers=pharmacist_headers)
    assert r3.status_code==403
    # doctor can approve after in_review
    r4 = client.post(f"/api/visits/{vid}/workflow/approve", json={}, headers=doctor_headers)
    assert r4.status_code==200
