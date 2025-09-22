# Airport API

Django REST API for airport operations (routes, flights, airplanes, crews, tickets).
Built with DRF, JWT auth, filtering, pagination, and OpenAPI docs via drf-spectacular.

## Features
- CRUD for core entities (Airport, Route, AirplaneType, Airplane, Crew, Flight, Order, Ticket)
- Filtering, search, ordering, pagination
- JWT authentication (SimpleJWT)
- Browsable API + OpenAPI docs (Swagger/Redoc)
- Custom endpoints:
  - `GET /api/flights/{id}/seats/` — seat map
  - `POST /api/flights/{id}/book/` — book a seat (atomic, unique per flight)

## Screenshots

> All screenshots are taken from the Browsable API and docs (local run).

### Database schema
![DB schema](./docs/db_schema.png)

### Browsable API
![API root](./docs/screen-api-root.png)
*Browsable API root (`/api/`).*

![Airports list](./docs/screen-airports-list.png)
*Airports list with pagination.*

![Airport detail](./docs/screen-airport-detail.png)
*Airport detail page.*

![Flights list](./docs/screen-flights-list.png)
*Flights list with filtering/ordering.*

### Custom endpoints
![Flight seats](./docs/screen-flight-seats.png)
*GET `/api/flights/{id}/seats/` seat map.*

### API Docs & Admin
![Swagger UI](./docs/screen-swagger.png)
*Swagger UI (`/api/docs/`).*

![Redoc](./docs/screen-redoc.png)
*Redoc (`/api/redoc/`).*

## Requirements
- Python 3.12+
- pip, virtualenv
- (Optional) Docker for PostgreSQL

## Docker (PostgreSQL)

```bash
# start (build images and run containers)
docker compose up --build

# stop
docker compose down
```

## Setup (local, SQLite)
```bash

python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell
# source .venv/bin/activate  # macOS/Linux

pip install --upgrade pip
pip install -r requirements.txt

cp .env.example .env
# By default SQLite will be used (no extra steps needed)

python manage.py migrate
python manage.py createsuperuser
python manage.py loaddata fixtures/seed.json  # optional
python manage.py runserver