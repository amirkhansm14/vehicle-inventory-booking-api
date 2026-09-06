# TODO — Containerized Deployment & CI/CD

Status: **done and verified**. The app is deployed on Railway, CI/CD is wired up
end-to-end, and a full green run (`test` → `deploy`) has actually happened —
this isn't just config that's expected to work, it's been exercised.

Live URL: https://vehicle-inventory-booking-api-production.up.railway.app/

This file exists so the two non-obvious gotchas hit while setting this up aren't
rediscovered the hard way if this ever needs to be redone (new account, new repo,
a future agent picking this up cold).

## What's set up

- Railway project `vehicle-inventory-booking-api` (workspace
  `amirkhansm14's Projects`): a Postgres service, and an app service linked to
  `amirkhansm14/vehicle-inventory-booking-api` on `main`, building from the
  `Dockerfile` (per `railway.json`).
- App service env vars: `DJANGO_ENV=production`, `SECRET_KEY` (generated,
  distinct from any value in this repo), `ALLOWED_HOSTS` (the Railway domain),
  `DATABASE_URL` (a live reference `${{Postgres.DATABASE_URL}}`, not a hardcoded
  copy), `CORS_ALLOWED_ORIGINS` (empty — no frontend yet).
- GitHub Actions secrets on the repo: `RAILWAY_TOKEN`, `RAILWAY_PROJECT_ID`,
  `RAILWAY_SERVICE_ID`.
- `.github/workflows/ci-cd.yml`: `test` runs on every PR into `main` and every
  push to `main`; `deploy` runs only on push to `main`, only after `test` passes.
  Confirmed both jobs green on a real push (PR #3 merge → run `34007935887`).

## Gotcha: Railway token type

Railway has two kinds of tokens and they are **not interchangeable**:

- A **project token** (created from within a project's own Settings → Tokens) is
  scoped to one project/environment and is read via the `RAILWAY_TOKEN` env var.
- An **account/personal API token** (created from Account Settings → Tokens,
  which is what got created here) is scoped to your whole account and must be
  passed as `RAILWAY_API_TOKEN`, not `RAILWAY_TOKEN` — the CLI rejects it under
  the wrong variable name with "Invalid RAILWAY_TOKEN".

`ci-cd.yml` passes the `RAILWAY_TOKEN` **secret** into the `RAILWAY_API_TOKEN`
**environment variable**, because the token that exists is an account token. If a
project-scoped token is generated instead in the future, swap that env var back
to `RAILWAY_TOKEN`.

Also note: the token's *value* is what the dashboard shows in the "we'll only
show this once" box at creation time (a UUID-looking string) — not the "Token ID"
column shown afterward in the tokens table, which looks similar but is a
different, unusable value.

## Gotcha: `railway up` needs an explicit `--project` in CI

`railway init` / `railway link` write the project link to local machine config
(outside the repo), not to a file that gets checked out. A fresh GitHub Actions
runner has no such link, so `railway up` fails with "No linked project found."
`ci-cd.yml` passes `--project "${{ secrets.RAILWAY_PROJECT_ID }}"` and
`--environment production` explicitly instead of relying on a link file.

## What's genuinely left

1. **(Recommended) Branch protection on `main`** — require the `test` job to pass
   before a PR can merge, so `deploy` can never ship untested code. Not done yet;
   nothing has depended on it so far because every merge so far went through a
   PR with a green `test` run first, but that's a habit, not an enforced rule.
2. **Screen recording deliverable** (2–5 min, per the original brief) — show the
   project running, API calls (Swagger UI or Postman), and a booking being
   created plus validated. This has to be recorded by a person; link it in
   `README.md`'s "Screen recording" section once done.

## Local verification before touching Railway (still valid for future changes)

```bash
cp .env.docker.example .env.docker   # edit SECRET_KEY if you want
docker compose up --build
curl http://localhost:8000/api/vehicles/
```

This proves the container + Postgres path works before redeploying to Railway, so
any failure there is a Railway config issue, not an app issue.

## Deliberately out of scope

- No staging environment / preview deployments per PR — only prod-on-`main` is
  wired up, matching what the original brief actually asked for (host the API
  somewhere). Add PR preview environments only if a future request calls for it.
- No authentication is added by this deployment work — see "Known limitations" in
  `README.md`, which predates it and still applies.
