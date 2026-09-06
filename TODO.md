# TODO — Containerized Deployment & CI/CD

Everything code-side (Dockerfile, `docker-compose.yml`, `railway.json`, GitHub
Actions pipeline) is already in this repo. What's listed here is the account-side
setup that has to be done by a human with Railway/GitHub access — an agent working
on this repo later doesn't have those credentials and shouldn't invent them. This
file exists so that work isn't lost between sessions.

## What's already built

- `Dockerfile` + `entrypoint.sh` — runs `migrate`, `collectstatic`, then `gunicorn`,
  as a non-root user, reading `$PORT` (Railway sets this at runtime).
- `.dockerignore`
- `docker-compose.yml` + `.env.docker.example` — local container testing against a
  real Postgres instance (mirrors production settings, not SQLite).
- `railway.json` — tells Railway to build from the `Dockerfile` and sets a health
  check against `/api/vehicles/`.
- `.github/workflows/ci-cd.yml`:
  - `test` job — runs on every PR into `main` **and** every push to `main`: spins
    up a real Postgres service container, runs `manage.py check`, `migrate`, then
    `pytest`.
  - `deploy` job — runs only on push to `main`, only after `test` passes; deploys
    to Railway via the Railway CLI (`railway up`).

## What still needs to be done manually (cannot be automated by an agent)

1. **Create the Railway project**
   - Sign in at railway.app, create a new project, add a Postgres plugin/service.
   - Add a second service for this app, pointed at this GitHub repo, with
     "Deploy from Dockerfile" (railway.json already declares this).

2. **Set production environment variables in the Railway service dashboard**
   - `DJANGO_ENV=production`
   - `SECRET_KEY` — a real generated secret, different from any value in this repo
   - `ALLOWED_HOSTS` — the Railway-provided domain (and any custom domain)
   - `DATABASE_URL` — Railway injects this automatically when you attach its
     Postgres plugin to the service; verify it's present, don't hardcode it
   - `CORS_ALLOWED_ORIGINS` — the frontend origin(s) allowed to call this API
   - Leave `SECURE_SSL_REDIRECT` unset (defaults to `True`) since Railway
     terminates TLS in front of the container

3. **Create a Railway API token and service ID for CI/CD**
   - Railway dashboard → Account Settings → Tokens → create a token
   - Get the service ID from the service's settings page
   - In the GitHub repo: Settings → Secrets and variables → Actions, add:
     - `RAILWAY_TOKEN`
     - `RAILWAY_SERVICE_ID`
   - Without these two secrets the `deploy` job in `ci-cd.yml` will fail — that's
     expected until they're added.

4. **(Recommended) Branch protection on `main`**
   - Require the `test` job from `ci-cd.yml` to pass before a PR can be merged, so
     the CD job never deploys code that hasn't been tested.

5. **After the first successful deploy**
   - Confirm `https://<railway-domain>/api/docs/` loads.
   - Update the "Live URL" placeholder in `README.md`'s Deployment section.
   - Record the screen-recording deliverable against the deployed URL (or
     localhost — either satisfies the brief), then update the "Recording"
     placeholder in `README.md`.

## Local verification before touching Railway

```bash
cp .env.docker.example .env.docker   # edit SECRET_KEY if you want
docker compose up --build
curl http://localhost:8000/api/vehicles/
```

This proves the container + Postgres path works before wiring it to a real cloud
account, so any failure at that point is a Railway config issue, not an app issue.

## Deliberately out of scope for this pass

- No staging environment / preview deployments per PR — only prod-on-`main` is
  wired up, matching what the original brief actually asked for (host the API
  somewhere). Add PR preview environments only if a future request calls for it.
- No authentication is added by this change — see the "Known limitations" section
  in `README.md`, which predates this containerization work and still applies.
