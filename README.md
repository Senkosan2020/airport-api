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

## Requirements
- Python 3.12+
- pip, virtualenv
- (Optional) Docker for PostgreSQL

## Setup (local, SQLite)
```bash
git clone <your-repo-url> airport-api
cd airport-api

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