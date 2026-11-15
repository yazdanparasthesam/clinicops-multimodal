#!/usr/bin/env python3
import sys, requests, pathlib
BASE = sys.argv[1] if len(sys.argv)>1 else "http://localhost:8000"
print(f"Seeding {BASE}")
# Create nurse, doctor, pharmacist
for email, role in [("nurse@example.com","nurse"),("doctor@example.com","doctor"),("pharmacist@example.com","pharmacist")]:
    requests.post(f"{BASE}/api/auth/register", json={"email":email,"password":"password123","role":role})
    print(f"register {email}")

def login(email):
    r=requests.post(f"{BASE}/api/auth/login", json={"email":email,"password":"password123"})
    return r.json()["access_token"]

nurse_t=login("nurse@example.com")
h={"Authorization":f"Bearer {nurse_t}"}
# Create visit
r=requests.post(f"{BASE}/api/visits", json={"patient_name":"Alex Rivera","patient_dob":"1982-03-14","allergies":"penicillin"}, headers=h)
vid=r.json()["id"]
print(f"visit {vid}")
# Patch vitals
requests.patch(f"{BASE}/api/visits/{vid}", json={"weight_kg":70,"height_cm":175,"systolic":142,"diastolic":92,"age":44,"sex":"male","creatinine":1.1,"dose_mg":600,"meds":"warfarin, aspirin","taken":22,"prescribed":30}, headers=h)
print("patched vitals (triggers R002,R003)")
# Upload fixtures if exist
for fpath, ctype in [("evidence/fixtures/lesion-sample.jpg","image/jpeg"), ("evidence/fixtures/demo-intake.csv","text/csv")]:
    p=pathlib.Path(fpath)
    if p.exists():
        with open(p,"rb") as f:
            requests.post(f"{BASE}/api/visits/{vid}/attachments", files={"file":(p.name,f,ctype)}, headers=h)
        print(f"uploaded {fpath}")
# Upload webm stub
requests.post(f"{BASE}/api/visits/{vid}/attachments", files={"file":("memo.webm",b"\x1a\x45\xdf\xa3 stub","audio/webm")}, headers=h)
print("uploaded memo.webm")
# AI drafts
requests.post(f"{BASE}/api/visits/{vid}/ai/vision-draft", json={}, headers=h)
requests.post(f"{BASE}/api/visits/{vid}/ai/transcribe", json={"transcript":"45yo male chest pain, Wells 2, plan ECG and D-dimer","confidence":0.88}, headers=h)
print("AI drafts done")
print(f"Done. Open http://localhost:3000/visits/{vid}")
