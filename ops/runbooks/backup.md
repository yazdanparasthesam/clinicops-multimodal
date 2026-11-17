# Runbook: Backup & Restore

**Neon (prod):** branch-based PITR is on by default for the project; for a logical dump:

```bash
pg_dump "$DATABASE_URL" -Fc -f "clinicops-multimodal-$(date +%F).dump"    # keep outside the repo
pg_restore -d "$DATABASE_URL" --clean --if-exists "clinicops-multimodal-<date>.dump"
```

**Compose (dev):** data lives in the `fs_pgdata` volume;
`docker run --rm -v clinicops-multimodal_fs_pgdata:/data -v $(pwd):/backup alpine tar czf /backup/pgdata.tgz -C /data .`

**What MUST NOT be backed up:** `.env` files (secrets) — they are re-creatable from
`.env.example` + the credential store notes in `security/credentials-handling.md`.

Cadence for the course project: one manual dump before each deployment milestone (M7+),
stored outside the repo; evidence line appended to `ops/runs/`.
