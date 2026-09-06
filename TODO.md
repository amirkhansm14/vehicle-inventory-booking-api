# TODO — Containerized Deployment & CI/CD

Everything code-side (Dockerfile, `docker-compose.yml`, `railway.json`, GitHub
Actions pipeline) is already in this repo, and the project is **already deployed**:
`https://vehicle-inventory-booking-api-production.up.railway.app/`. This file
tracks what was done, what's left, and one gotcha worth remembering if this ever
needs to be redone.

## Status: done

- Railway project `vehicle-inventory-booking-api` created (workspace
  `amirkhansm14's Projects`), with a Postgres service and an app service linked
  to `amirkhansm14/vehicle-inventory-booking-api` on `main`, building from the
  `Dockerfile`.
- App service env vars set: `DJANGO_ENV=production`, `SECRET_KEY` (generated,
  distinct from any value in this repo), `ALLOWED_HOSTS` (the generated Railway
  domain), `DATABASE_URL` (set as a live reference `${{Postgres.DATABASE_URL}}`,
  not a hardcoded copy), `CORS_ALLOWED_ORIGINS` (empty — no frontend yet).
- Public domain generated:
  `vehicle-inventory-booking-api-production.up.railway.app`.
- GitHub Actions secrets `RAILWAY_TOKEN` and `RAILWAY_SERVICE_ID` set on the repo.
- First deploy done manually via `railway up` to prove the Dockerfile path works;
  `/api/vehicles/` and `/api/docs/` both return 200 on the live URL.

## Gotcha: Railway token type

Railway has two kinds of tokens and they are **not interchangeable**:

- A **project token** (created from within a project's own Settings → Tokens) is
  scoped to one project/environment and is read via the `RAILWAY_TOKEN` env var.
- An **account/personal API token** (created from Account Settings → Tokens,
  which is what got created here) is scoped to your whole account and must be
  passed as `RAILWAY_API_TOKEN`, not `RAILWAY_TOKEN` — the CLI rejects it under
  the wrong variable name with "Invalid RAILWAY_TOKEN".

This repo's `.github/workflows/ci-cd.yml` passes the `RAILWAY_TOKEN` **secret**
into the `RAILWAY_API_TOKEN` **environment variable**, because the token that
exists is an account token. If a project-scoped token is generated instead in the
future, swap that env var back to `RAILWAY_TOKEN` in the workflow.

Also note: the token's *value* is what the dashboard shows in the "we'll only
show this once" box at creation time (a UUID-looking string) — not the "Token ID"
column shown afterward in the tokens table, which looks similar but is a
different, unusable value.

## Gotcha: `railway up` needs an explicit `--project` in CI

`railway init` / `railway link` write the project link to local machine config
(outside the repo), not to a file that gets checked out. A fresh GitHub Actions
runner has no such link, so `railway up` fails with "No linked project found."
The workflow now passes `--project "${{ secrets.RAILWAY_PROJECT_ID }}"` and
`--environment production` explicitly instead of relying on a link file. The
project ID is stored as the `RAILWAY_PROJECT_ID` GitHub secret (not sensitive on
its own, but kept alongside the other Railway secrets for consistency):
`648bdcf2-eeae-4611-8b72-5c52c9f8c21a`.

## What's left

1. **Verify the GitHub Actions `deploy` job succeeds**, not just the manual
   `railway up` done from this session. Push a small change to `main` (or re-run
   the existing workflow) and check the `Deploy to Railway` job passes end to end.
2. **(Recommended) Branch protection on `main`** — require the `test` job to pass
   before a PR can merge, so `deploy` never ships untested code.
3. **Update `README.md`**:
   - Live URL is already known:
     `https://vehicle-inventory-booking-api-production.up.railway.app/` — put
     this in the "Live URL" placeholder in the Deployment section.
   - Record the screen-recording deliverable (2-5 min) against this live URL or
     localhost, then update the "Recording" placeholder.

## Local verification before touching Railway (still valid for future changes)

```bash
cp .env.docker.example .env.docker   # edit SECRET_KEY if you want
docker compose up --build
curl http://localhost:8000/api/vehicles/
```

This proves the container + Postgres path works before redeploying to Railway, so
any failure there is a Railway config issue, not an app issue.

## Deliberately out of scope for this pass

- No staging environment / preview deployments per PR — only prod-on-`main` is
  wired up, matching what the original brief actually asked for (host the API
  somewhere). Add PR preview environments only if a future request calls for it.
- No authentication is added by this change — see the "Known limitations" section
  in `README.md`, which predates this containerization work and still applies.
