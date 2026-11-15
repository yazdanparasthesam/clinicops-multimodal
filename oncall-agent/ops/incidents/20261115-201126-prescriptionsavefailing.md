# Incident 2026-11-15T20:11:26.884422 — PrescriptionSaveFailing

Alert: {'labels': {'alertname': 'PrescriptionSaveFailing'}}

Result: ESCALATED

Logs:
````
$ docker restart clinicops-multimodal-backend-1

/bin/sh: 1: docker: not found
 rc=127
$ curl -sf http://backend:8000/healthz

 rc=6
````
