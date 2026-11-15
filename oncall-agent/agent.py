from fastapi import FastAPI, Request
import datetime, pathlib, subprocess, os
app = FastAPI()

REPORT_DIR = pathlib.Path(os.getenv("ONCALL_REPORT_DIR","./ops/incidents"))
REPORT_DIR.mkdir(parents=True, exist_ok=True)

ALLOWLIST = {
    "PrescriptionSaveFailing": ["docker restart clinicops-multimodal-backend-1","curl -sf http://backend:8000/healthz"],
    "ImageAnalysisFailing": ["docker restart clinicops-multimodal-backend-1"],
    "HighLatencyVisit": ["curl -sf http://backend:8000/metrics | head -n 50"],
    "TranscriptionStuck": ["python scripts/requeue_attachments.py","curl -sf http://backend:8000/healthz"],
}

def run_allowlisted(alertname: str):
    cmds = ALLOWLIST.get(alertname, ["echo no-runbook"])
    logs=[]
    ok=True
    for cmd in cmds:
        # strict check: must be in allowlist exactly
        allowed = any(cmd.strip()==a for a in sum(ALLOWLIST.values(), []))
        if not allowed:
            logs.append(f"BLOKED (126): {cmd}")
            ok=False; break
        try:
            # In Compose env docker sock available; in local test stub
            proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            logs.append(f"$ {cmd}\n{proc.stdout[:2000]}\n{proc.stderr[:2000]} rc={proc.returncode}")
            if proc.returncode!=0: ok=False
        except Exception as e:
            logs.append(f"error {e}"); ok=False
    return ok, logs

@app.post("/webhook")
async def webhook(req: Request):
    body=await req.json()
    alerts=body.get("alerts",[])
    for al in alerts:
        name=al.get("labels",{}).get("alertname","Unknown")
        ok, logs = run_allowlisted(name)
        report = f"# Incident {datetime.datetime.utcnow().isoformat()} — {name}\n\nAlert: {al}\n\nResult: {'RECOVERED' if ok else 'ESCALATED'}\n\nLogs:\n````\n" + "\n".join(logs) + "\n````\n"
        path = REPORT_DIR / f"{datetime.datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-{name.lower()}.md"
        path.write_text(report)
        print(report)
    return {"ok": True}

@app.get("/healthz")
def healthz(): return {"status":"ok"}

if __name__=="__main__":
    import uvicorn; uvicorn.run(app, host="0.0.0.0", port=8090)
