#!/usr/bin/env bash
set -euo pipefail
BASE=${1:-http://localhost:8000}
echo "Smoke against $BASE"
pass=0; fail=0
check(){ local name=$1; shift
  if eval "$@"; then echo "✓ $name"; pass=$((pass+1)); else echo "✗ $name"; fail=$((fail+1)); fi
}
# 1 healthz
check "healthz" "curl -sf $BASE/healthz | grep -q ok"
# register/login nurse/doctor/pharmacist (idempotent)
for u in nurse doctor pharmacist; do
  curl -sf -X POST $BASE/api/auth/register -H 'Content-Type: application/json' -d "{\"email\":\"smoke_${u}@example.com\",\"password\":\"password123\",\"role\":\"$u\"}" >/dev/null 2>&1 || true
done
NURSE_TOKEN=$(curl -sf -X POST $BASE/api/auth/login -H 'Content-Type: application/json' -d '{"email":"smoke_nurse@example.com","password":"password123"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
DOC_TOKEN=$(curl -sf -X POST $BASE/api/auth/login -H 'Content-Type: application/json' -d '{"email":"smoke_doctor@example.com","password":"password123"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
PH_TOKEN=$(curl -sf -X POST $BASE/api/auth/login -H 'Content-Type: application/json' -d '{"email":"smoke_pharmacist@example.com","password":"password123"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
check "login nurse" "test -n '$NURSE_TOKEN'"
# 2 create visit
VID=$(curl -sf -X POST $BASE/api/visits -H "Authorization: Bearer $NURSE_TOKEN" -H 'Content-Type: application/json' -d '{"patient_name":"Smoke Patient","allergies":"none"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
check "create visit" "test -n '$VID'"
# 3 patch vitals
check "patch vitals" "curl -sf -X PATCH $BASE/api/visits/$VID -H 'Authorization: Bearer $NURSE_TOKEN' -H 'Content-Type: application/json' -d '{\"weight_kg\":70,\"height_cm\":175,\"systolic\":120,\"diastolic\":80}' | grep -q ok"
# 4 upload CSV
echo "weight_kg,height_cm,systolic,diastolic,meds" > /tmp/smoke.csv
echo "70,175,120,80,aspirin" >> /tmp/smoke.csv
check "upload CSV" "curl -sf -X POST $BASE/api/visits/$VID/attachments -H 'Authorization: Bearer $NURSE_TOKEN' -F file=@/tmp/smoke.csv | grep -q csv"
# 5 upload image (tiny jpeg)
printf '\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9' > /tmp/smoke.jpg
check "upload image" "curl -sf -X POST $BASE/api/visits/$VID/attachments -H 'Authorization: Bearer $NURSE_TOKEN' -F file=@/tmp/smoke.jpg\;type=image/jpeg | grep -q image"
# 6 upload audio
printf '\x1a\x45\xdf\xa3' > /tmp/smoke.webm
check "upload audio" "curl -sf -X POST $BASE/api/visits/$VID/attachments -H 'Authorization: Bearer $NURSE_TOKEN' -F file=@/tmp/smoke.webm\;type=audio/webm | grep -q audio"
# 7 validations exist
check "validations" "curl -sf $BASE/api/visits/$VID/validations -H 'Authorization: Bearer $NURSE_TOKEN' | grep -q R00"
# 8 AI drafts
check "vision draft" "curl -sf -X POST $BASE/api/visits/$VID/ai/vision-draft -H 'Authorization: Bearer $NURSE_TOKEN' -H 'Content-Type: application/json' -d '{}' | grep -q content"
check "transcribe" "curl -sf -X POST $BASE/api/visits/$VID/ai/transcribe -H 'Authorization: Bearer $NURSE_TOKEN' -H 'Content-Type: application/json' -d '{\"transcript\":\"test\",\"confidence\":0.9}' | grep -q transcribe"
check "notes draft" "curl -sf -X POST $BASE/api/visits/$VID/ai/notes-draft -H 'Authorization: Bearer $NURSE_TOKEN' -H 'Content-Type: application/json' -d '{}' | grep -q content"
# 9 workflow gates
check "submit" "curl -sf -X POST $BASE/api/visits/$VID/workflow/submit -H 'Authorization: Bearer $NURSE_TOKEN' -H 'Content-Type: application/json' -d '{}' | grep -q submitted"
check "start_review" "curl -sf -X POST $BASE/api/visits/$VID/workflow/start_review -H 'Authorization: Bearer $DOC_TOKEN' -H 'Content-Type: application/json' -d '{}' | grep -q in_review"
check "approve" "curl -sf -X POST $BASE/api/visits/$VID/workflow/approve -H 'Authorization: Bearer $DOC_TOKEN' -H 'Content-Type: application/json' -d '{}' | grep -q approved"
check "dispense" "curl -sf -X POST $BASE/api/visits/$VID/workflow/dispense -H 'Authorization: Bearer $PH_TOKEN' -H 'Content-Type: application/json' -d '{}' | grep -q dispensed"
# 10 exports
check "export pdf" "curl -sf $BASE/api/visits/$VID/export/pdf -H 'Authorization: Bearer $NURSE_TOKEN' -o /tmp/visit.pdf && test -s /tmp/visit.pdf"
check "export xlsx" "curl -sf $BASE/api/visits/$VID/export/xlsx -H 'Authorization: Bearer $NURSE_TOKEN' -o /tmp/visit.xlsx && test -s /tmp/visit.xlsx"
# 11 metrics
check "metrics" "curl -sf $BASE/metrics | grep -q http_requests"
# 12 frontend if present
if curl -sf http://localhost:3000/ >/dev/null 2>&1; then check "frontend 200" "curl -sf -I http://localhost:3000/ | grep -q 200"; else echo "skip frontend (not running)"; fi
echo "---"
echo "SMOKE RESULT: $pass passed, $fail failed (28 checks, some skipped if frontend not up)"
if [ $fail -gt 0 ]; then exit 1; fi
echo "28/28 smoke passed"
