import pytest
pytestmark = pytest.mark.integration

def test_create_and_list(client, auth_headers):
    r = client.post("/api/visits", json={"patient_name":"John Doe","patient_dob":"1980-01-01"}, headers=auth_headers)
    assert r.status_code==200, r.text
    vid = r.json()["id"]
    r2 = client.get("/api/visits", headers=auth_headers)
    assert r2.status_code==200
    assert any(v["id"]==vid for v in r2.json())

def test_patch_and_scores(client, auth_headers):
    r = client.post("/api/visits", json={"patient_name":"Jane"}, headers=auth_headers)
    vid = r.json()["id"]
    r2 = client.patch(f"/api/visits/{vid}", json={"weight_kg":70,"height_cm":175,"systolic":120,"diastolic":80,"age":40,"creatinine":1.0,"sex":"male","dose_mg":100,"taken":28,"prescribed":30}, headers=auth_headers)
    assert r2.status_code==200
    # scores should be computed
    r3 = client.get(f"/api/visits/{vid}", headers=auth_headers)
    assert r3.json()["scores"] is not None
    assert r3.json()["scores"]["bmi"] == 22.9

def test_workflow_gates(client, auth_headers, doctor_headers):
    # create with missing vitals → R008 error blocks submit
    r = client.post("/api/visits", json={"patient_name":"Gate Test"}, headers=auth_headers)
    vid = r.json()["id"]
    # patch minimal but missing required vitals? We'll test submit blocked when allergy error present
    client.patch(f"/api/visits/{vid}", json={"weight_kg":70,"height_cm":175,"systolic":120,"diastolic":80,"meds":"penicillin","allergies":"penicillin"}, headers=auth_headers)
    # trigger recompute already done in patch
    r2 = client.post(f"/api/visits/{vid}/workflow/submit", json={}, headers=auth_headers)
    # R001 allergy is error → should be 422
    assert r2.status_code==422, r2.text
    # fix allergy and retry
    client.patch(f"/api/visits/{vid}", json={"allergies":"none"}, headers=auth_headers)
    r3 = client.post(f"/api/visits/{vid}/workflow/submit", json={}, headers=auth_headers)
    assert r3.status_code==200

def test_multimodal_upload(client, auth_headers):
    r = client.post("/api/visits", json={"patient_name":"Multi Test"}, headers=auth_headers)
    vid = r.json()["id"]
    # CSV upload
    csv_content = b"weight_kg,height_cm,systolic,diastolic,meds\n70,175,120,80,aspirin"
    r2 = client.post(f"/api/visits/{vid}/attachments", files={"file":("intake.csv", csv_content, "text/csv")}, headers=auth_headers)
    assert r2.status_code==200, r2.text
    assert r2.json()["kind"]=="csv"
    # image upload (minimal JPEG header)
    jpg = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9"
    r3 = client.post(f"/api/visits/{vid}/attachments", files={"file":("wound.jpg", jpg, "image/jpeg")}, headers=auth_headers)
    assert r3.status_code==200
    # audio
    webm = b"\x1a\x45\xdf\xa3 fake webm data"
    r4 = client.post(f"/api/visits/{vid}/attachments", files={"file":("memo.webm", webm, "audio/webm")}, headers=auth_headers)
    assert r4.status_code==200
    # invalid mime rejected
    r5 = client.post(f"/api/visits/{vid}/attachments", files={"file":("evil.exe", b"MZ", "application/octet-stream")}, headers=auth_headers)
    assert r5.status_code==400
