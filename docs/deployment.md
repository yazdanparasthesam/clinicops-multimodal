# Deployment & CI/CD

## Targets 

- **Dev API:** FastAPI Cloud `clinicops-dev-api` → `https://clinicops-dev-api.fastapicloud.dev`
- **Dev Web:** Vercel `clinicops-dev-web` → `https://clinicops-dev-web.vercel.app`
- **Prod API:** FastAPI Cloud `clinicops-prod-api` → `https://clinicops-prod-api.fastapicloud.dev` (Neon prod branch)
- **Prod Web:** Vercel `clinicops-prod-web` → `https://clinicops-prod-web.vercel.app`
- **DB:** Neon Postgres (dev branch `dev`, prod branch `production`) + pooled connection

## CI/CD

| Workflow | Trigger | What it does |
|---|---|---|
| `ci.yml` | PR + push on main | ruff + pytest (unit+integration+contract) + vitest + openapi drift + gitleaks |
| `deploy.yml` | push main after CI green | deploy API to FastAPI Cloud (dev), smoke, then deploy Web to Vercel dev |
| `promote-prod.yml` | manual `workflow_dispatch` | requires `production` environment approval → deploy API prod + smoke + deploy Web prod |
| `rollback.yml` | manual | reverts prod to previous Vercel deployment + previous API image |

## Secrets

- Repo: `FASTAPI_CLOUD_DEV_TOKEN`, `VERCEL_DEV_TOKEN`
- Environment `production`: `FASTAPI_CLOUD_PROD_TOKEN`, `VERCEL_PROD_TOKEN`, `DATABASE_URL_PROD`, `JWT_SECRET_PROD` + Vercel project/team IDs
- App runtime: `DATABASE_URL`, `JWT_SECRET`, `GEMINI_API_KEY` (optional), `CORS_ORIGINS`

**Rotate non-expiring Vercel token before prod dispatch** — see runbook.

## Verification

```bash
curl https://clinicops-dev-api.fastapicloud.dev/healthz
curl -I https://clinicops-dev-web.vercel.app/
bash ops/smoke.sh https://clinicops-dev-api.fastapicloud.dev
```

Prod dispatch evidence in `evidence/curated/08-prod-dispatched.png` showing `deploy-prod: succeeded` (not skipped).
