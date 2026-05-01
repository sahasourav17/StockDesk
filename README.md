# Django Stock Management System

## Quick start

1. Copy env file:
   - `cp .env.example .env`
2. Install dependencies:
   - `uv sync`
3. Run migrations:
   - `uv run python manage.py migrate`
4. Create admin user:
   - `uv run python manage.py createsuperuser`
5. Start app:
   - `uv run python manage.py runserver`

## Docker

- `docker compose up --build`

## Architecture

- Service layer handles business rules in `apps/*/services.py`
- Selectors provide reporting and stock query logic
- Ledger stock model based on `StockTransaction`
