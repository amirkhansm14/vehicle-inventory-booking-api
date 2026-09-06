# Vehicle Inventory & Booking API

A Django REST Framework API for managing a vehicle inventory and creating
date-validated, auto-priced bookings against it. Built for the Django Developer
Backend Task (see [`REQUIREMENTS.md`](REQUIREMENTS.md) for the full requirements
extracted from the brief, and the "Engineering decisions" section there for a few
judgment calls made where the brief was ambiguous).

## Tech stack

- Python 3.11+, Django 5, Django REST Framework
- `django-filter` for query-param filtering
- `drf-spectacular` for OpenAPI schema + Swagger UI
- `django-environ` / `dj-database-url` for 12-factor config
- SQLite in development, PostgreSQL in production
- `pytest` + `pytest-django` + `factory_boy` for tests

## Project structure

```
vehicle_system/
  settings/
    base.py          # shared settings
    development.py    # local dev (SQLite, debug on)
    production.py     # deploy target (Postgres, hardened security)
  urls.py
inventory/
  models.py           # Vehicle, Booking + DB constraints/indexes
  validators.py        # reusable field validators
  serializers.py        # request/response shape + field-level validation
  services/
    booking_service.py  # booking business logic (overlap check, pricing, locking)
  exceptions.py         # domain exceptions -> DRF error responses
  filters.py             # vehicle query-param filters
  views.py                # thin viewsets
  urls.py
  admin.py
  tests/                  # pytest suite + factories
```

Business logic (overlap detection, pricing, availability toggling) lives in
`inventory/services/booking_service.py`, not in the serializer or view, so it can be
tested and reused independently of the HTTP layer.

## Setup

### 1. Prerequisites

- Python 3.11+
- (Optional, production only) PostgreSQL

### 2. Clone and create a virtual environment

```bash
git clone <your-repo-url>
cd "Vehicle Inventory & Booking API"
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Then edit `.env`:

- `SECRET_KEY` — generate one with:
  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```
- Leave `DATABASE_URL` empty for local development (falls back to a `db.sqlite3`
  file automatically).

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. (Optional) Create an admin user

```bash
python manage.py createsuperuser
```

### 7. Run the project

```bash
python manage.py runserver
```

The API is now available at `http://127.0.0.1:8000/api/`.

## How to test the API

### Automated tests

```bash
pytest
```

### Interactively

- **Swagger UI**: `http://127.0.0.1:8000/api/docs/` — browse and try every endpoint.
- **OpenAPI schema**: `http://127.0.0.1:8000/api/schema/`
- **Django admin**: `http://127.0.0.1:8000/admin/` (after `createsuperuser`)
- **Postman**: import `postman_collection.json` from the repo root; it includes one
  request per endpoint plus the overlap-rejection and validation-error cases.

## API endpoints

### Vehicles

| Method | URL | Description |
|---|---|---|
| GET | `/api/vehicles/` | List vehicles (paginated) |
| POST | `/api/vehicles/` | Create a vehicle |
| GET | `/api/vehicles/{id}/` | Retrieve a vehicle |
| PUT | `/api/vehicles/{id}/` | Update a vehicle |
| PATCH | `/api/vehicles/{id}/` | Partially update a vehicle |
| DELETE | `/api/vehicles/{id}/` | Delete a vehicle |

Filtering (combinable):

- `GET /api/vehicles/?brand=Toyota`
- `GET /api/vehicles/?fuel_type=Electric`
- `GET /api/vehicles/?is_available=true`

### Bookings

| Method | URL | Description |
|---|---|---|
| GET | `/api/bookings/` | List bookings (paginated) |
| POST | `/api/bookings/` | Create a booking (runs all business rules) |
| GET | `/api/bookings/{id}/` | Retrieve a booking |

Bookings intentionally have no update/delete endpoint — the brief only asks for
list/create/retrieve, and a booking's dates and price are not meant to be edited
after the fact.

## Sample requests

### Create a vehicle

```bash
curl -X POST http://127.0.0.1:8000/api/vehicles/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Corolla",
    "brand": "Toyota",
    "year": 2023,
    "price_per_day": "50.00",
    "fuel_type": "petrol"
  }'
```

### Create a booking

```bash
curl -X POST http://127.0.0.1:8000/api/bookings/ \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle": 1,
    "customer_name": "Jane Doe",
    "customer_phone": "9876543210",
    "start_date": "2026-09-10",
    "end_date": "2026-09-13"
  }'
```

Response:

```json
{
  "id": 1,
  "vehicle": {
    "id": 1,
    "name": "Corolla",
    "brand": "Toyota",
    "fuel_type": "petrol",
    "price_per_day": "50.00"
  },
  "customer_name": "Jane Doe",
  "customer_phone": "9876543210",
  "start_date": "2026-09-10",
  "end_date": "2026-09-13",
  "total_amount": "150.00",
  "created_at": "2026-09-06T02:00:49.734548Z"
}
```

`total_amount` is always computed server-side as `(end_date - start_date).days *
price_per_day` — clients cannot set it.

### Validation error examples

Overlapping booking:

```json
{ "vehicle": ["This vehicle is already booked for an overlapping date range."] }
```

Invalid phone number:

```json
{ "customer_phone": ["Phone number must be exactly 10 digits."] }
```

Past start date:

```json
{ "start_date": ["Date cannot be in the past."] }
```

## Business rules implemented

- A vehicle cannot have two bookings with overlapping date ranges (enforced inside
  a locked database transaction — see `booking_service.create_booking` — so
  concurrent requests can't race past the check).
- `total_amount` is always `(end_date - start_date).days * price_per_day`.
- `start_date` cannot be before today.
- `end_date` must be strictly after `start_date` (enforced at both the serializer
  and the database, via a `CheckConstraint`).
- `customer_phone` must be exactly 10 digits (enforced at both the serializer and
  the database field validator).
- Once a booking is created, `Vehicle.is_available` is set to `False`.

## Running with Docker

```bash
cp .env.docker.example .env.docker   # edit SECRET_KEY before real use
docker compose up --build
```

This builds the app image from the `Dockerfile`, starts a real Postgres container,
runs migrations + `collectstatic`, and serves the API at `http://localhost:8000/`.
It runs the *production* settings module (with `SECURE_SSL_REDIRECT=False` since
there's no TLS on localhost), so it's a faithful test of the deployment path.

## Deployment (Railway, containerized)

The project is set up to deploy as a container on Railway:

- `Dockerfile` / `entrypoint.sh` — builds the app image and runs
  `migrate` → `collectstatic` → `gunicorn` on container start.
- `railway.json` — tells Railway to build from the Dockerfile and health-check
  `/api/vehicles/`.
- `.github/workflows/ci-cd.yml` — a GitHub Actions pipeline with two jobs:
  - **`test`** — runs on every pull request into `main` and every push to `main`:
    spins up a Postgres service, runs `manage.py check`, migrations, then the
    `pytest` suite.
  - **`deploy`** — runs only on push to `main`, only after `test` passes: deploys
    the current commit to Railway via the Railway CLI.

This is the same setup as any other platform (`Procfile` is also kept for
Heroku-style buildpack platforms as a fallback), but Railway is the primary,
documented target.

**Creating the Railway project, Postgres instance, API token, and GitHub Actions
secrets (`RAILWAY_TOKEN`, `RAILWAY_SERVICE_ID`) all require an actual Railway/GitHub
account and cannot be done from inside this repository.** The full manual
checklist — what to click, which env vars to set on Railway, which secrets to add
on GitHub — is in [`TODO.md`](TODO.md). Once deployed:

- API: `https://<your-railway-domain>/api/...`
- Swagger UI: `https://<your-railway-domain>/api/docs/`

**Live URL:** https://vehicle-inventory-booking-api-production.up.railway.app/

## Screen recording

A 2–5 minute recording showing the project running, API calls against it (Swagger
UI or Postman), and a booking being created plus validated against the business
rules above is a required deliverable. Record this yourself after running through
the "How to test the API" section above, then link it here:

**Recording:** _TODO — add YouTube/Drive link here_

## Known limitations / out of scope

- No authentication — the brief did not request one, so every endpoint is
  currently open. Add DRF token or session authentication before using this in a
  real deployment with untrusted clients.
- No booking cancellation endpoint (would be the natural way to make a vehicle
  available again); not requested by the brief.
- `Vehicle.is_available` is set to `False` on the first booking as the brief
  literally states, while the authoritative "can this be booked for these dates"
  check is the overlap query — see `REQUIREMENTS.md` for why both exist.
