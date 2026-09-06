# Requirements — Vehicle Inventory & Booking API

Extracted from `Ai and Python Django Intern Task.pdf`. This document is the single
source of truth for what was asked; implementation decisions that fill gaps in the
brief are called out explicitly under **Engineering decisions**.

## Objective

A Django REST Framework API to manage a vehicle inventory and bookings against it,
with server-side validation and pricing logic, ready to be consumed by a frontend or
another backend service.

## Project layout (mandated)

- Django project: `vehicle_system`
- Django app: `inventory`

## Data model

### Vehicle

| Field | Type | Notes |
|---|---|---|
| name | CharField | |
| brand | CharField | filterable |
| year | IntegerField | |
| price_per_day | DecimalField | > 0 |
| fuel_type | CharField + choices | Petrol, Diesel, Electric, Hybrid; filterable |
| is_available | BooleanField | default `True`; filterable |

### Booking

| Field | Type | Notes |
|---|---|---|
| vehicle | ForeignKey → Vehicle | |
| customer_name | CharField | |
| customer_phone | CharField | exactly 10 digits |
| start_date | DateField | cannot be in the past |
| end_date | DateField | must be after start_date |
| total_amount | DecimalField | auto-calculated, read-only to clients |

## Business rules

1. A vehicle cannot have two bookings with overlapping date ranges.
2. `total_amount = number_of_days * price_per_day`, computed server-side.
3. `start_date` cannot be before today.
4. `end_date` must be strictly after `start_date`.
5. `customer_phone` must be exactly 10 digits.
6. Once a booking is created, the vehicle becomes unavailable
   (`is_available = False`).

## API surface

### Vehicles

- `GET /api/vehicles/` — list, filterable
- `POST /api/vehicles/` — create
- `GET /api/vehicles/{id}/` — retrieve
- `PUT /api/vehicles/{id}/` / `PATCH` — update
- `DELETE /api/vehicles/{id}/` — delete

Filters: `?brand=`, `?fuel_type=`, `?is_available=`

### Bookings

- `GET /api/bookings/` — list
- `POST /api/bookings/` — create (runs all business rules)
- `GET /api/bookings/{id}/` — retrieve

No update/delete endpoint was requested for bookings — a booking is either created
or (out of scope) cancelled through a future dedicated action, not a raw PATCH/DELETE.

## Deliverables (from the brief)

1. Complete Django project code (models, serializers, views, urls, settings).
2. `.env.example` with dummy DB/secret values.
3. `README.md` with setup, migrations, run instructions, API testing instructions,
   endpoint list, and a sample booking JSON payload.
4. A 2–5 minute screen recording of the running project and API tests — **this is a
   human deliverable**: an agent cannot operate a screen recorder or a Postman GUI
   session on the user's behalf, so this repository ships everything needed to
   record it (Swagger UI, a Postman collection, seed data) but the recording itself
   must be done by the person submitting the task.
5. Hosting the API on a cloud platform — **this requires the submitter's own cloud
   account/credentials**, which an agent does not have. The project is made
   deployment-ready (Procfile, `gunicorn`, `whitenoise`, `DATABASE_URL` support,
   production settings module) with step-by-step deploy instructions in the README,
   but the actual deploy/account creation is left to the submitter.

## Engineering decisions (gaps the brief leaves open)

- **`is_available` vs. overlap checking**: the brief says a booked vehicle "becomes
  unavailable," but also implies bookings have date ranges and only *overlapping*
  ones should be rejected — a strict reading of "unavailable forever after one
  booking" would make the overlap rule pointless (a vehicle could never be booked
  twice, overlapping or not). The overlap check against existing bookings is treated
  as the authoritative availability rule; `is_available` is kept as the literal,
  simple flag the spec asks for and is flipped to `False` on booking creation as
  instructed, with a note in the README about this tension so a reviewer can see it
  was a deliberate, documented call rather than an oversight.
- **Race conditions**: overlap checking + booking creation is wrapped in a DB
  transaction with a row lock on the vehicle to prevent two concurrent requests from
  double-booking the same vehicle.
- **Auth**: not mentioned in the brief, so no authentication is implemented. Every
  endpoint is open, matching the scope given. Called out in the README as a
  deliberate omission.
- **Soft vs. hard delete, booking cancellation, dynamic pricing, multi-currency,
  etc.**: none of this is in the brief; none of it is built. Keeping scope to what
  was asked.
