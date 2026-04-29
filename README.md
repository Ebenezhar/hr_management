# HR Management (Django)

Small Django project scaffolding for an HR management system. It contains a single app (`employees`) with an `EmployeeRecord` model, SQLite for local development, and a small REST API (Django REST Framework) under `/api/`.

## What’s in this repo

- **Django project**: `config/`
- **Employees app**: `employees/`
- **Database (local/dev)**: `db.sqlite3`

## Tech stack

- **Python**: (use your local Python in `.venv`)
- **Django**: 5.2.x (project was generated with Django 5.2.13)
- **API**: Django REST Framework (DRF)
- **DB**: SQLite (default Django dev database)

## Quickstart (Windows / PowerShell)

If you already have the virtual environment created in `.venv`, activate it:

```bash
.venv\Scripts\Activate.ps1
```

Install dependencies (if not installed yet). If you don’t have a `requirements.txt` in this repo yet, install Django + DRF directly:

```bash
python -m pip install --upgrade pip
python -m pip install "Django>=5.2,<6" djangorestframework
```

Run migrations and start the server:

```bash
python manage.py migrate
python manage.py runserver
```

Open:

- **Admin**: `http://127.0.0.1:8000/admin/`
- **API base**: `http://127.0.0.1:8000/api/`

Create an admin user if needed:

```bash
python manage.py createsuperuser
```

## Current data model

The main model lives in `employees/models.py`:

- **EmployeeRecord**
  - `full_name` (string)
  - `job_title` (string)
  - `country` (string)
  - `salary` (decimal)

The corresponding migrations are in `employees/migrations/`:

- `0001_initial.py` creates the model (originally named `Employee`)
- `0002_rename_employee_employeerecord.py` renames it to `EmployeeRecord`

## Current routes / UI

`config/urls.py` routes:

- `/admin/`
- `/api/` (includes `employees/urls.py`)

The API is implemented using DRF `APIView`s in `employees/views.py`.

## API endpoints

All endpoints are prefixed with `/api/`.

### Employee CRUD

- `GET /api/employees/` — list employees
- `POST /api/employees/` — create employee

Example create:

```bash
curl -X POST "http://127.0.0.1:8000/api/employees/" ^
  -H "Content-Type: application/json" ^
  -d "{\"full_name\":\"Jane Doe\",\"job_title\":\"Software Engineer\",\"country\":\"India\",\"salary\":\"100000.00\"}"
```

Example list:

```bash
curl "http://127.0.0.1:8000/api/employees/"
```

### Salary details (tax deduction calculation)

- `GET /api/employees/<employee_id>/salary-details/` — returns salary, tax rate, tax deduction, net salary (all 2dp)

Example:

```bash
curl "http://127.0.0.1:8000/api/employees/1/salary-details/"
```

### Metrics / reporting

- `GET /api/employees/metrics/country/<country>/` — min/max/avg + tax rate + avg after tax
- `GET /api/employees/metrics/job-title/<title>/` — average salary for a job title

Examples:

```bash
curl "http://127.0.0.1:8000/api/employees/metrics/country/India/"
curl "http://127.0.0.1:8000/api/employees/metrics/job-title/Software%20Engineer/"
```

## Tests

There is a starter test file at `employees/tests.py`, but it needs fixing before it will run cleanly (it references `Employee` while the model is now `EmployeeRecord`).

Run tests:

```bash
python manage.py test
```

## Repo layout

```text
hr_management/
  config/
    settings.py
    urls.py
    asgi.py
    wsgi.py
  docs/
    context_skills.md
  employees/
    migrations/
    models.py
    views.py
    admin.py
    tests.py
    apps.py
  manage.py
  db.sqlite3
  README.md
```

## Next steps (recommended)

If you want this to behave like a real HR system, the usual next increments are:

- **Admin integration**: register `EmployeeRecord` in `employees/admin.py`
- **Permissions**: restrict API access (auth, staff-only, roles)
- **More CRUD**: retrieve/update/delete endpoints, filtering, pagination
- **Validation & constraints**: salary rules, country normalization, etc.
- **Tests**: fix + expand tests for API and calculation/metrics endpoints
- **Docs**: see `docs/context_skills.md` for a capability/skills checklist