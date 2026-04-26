# HR Management (Django)

Small Django project scaffolding for an HR management system. Currently it contains a single app (`employees`) with an `EmployeeRecord` model and uses SQLite for local development.

## What’s in this repo

- **Django project**: `config/`
- **Employees app**: `employees/`
- **Database (local/dev)**: `db.sqlite3`

## Tech stack

- **Python**: (use your local Python in `.venv`)
- **Django**: 5.2.x (project was generated with Django 5.2.13)
- **DB**: SQLite (default Django dev database)

## Quickstart (Windows / PowerShell)

If you already have the virtual environment created in `.venv`, activate it:

```bash
.venv\Scripts\Activate.ps1
```

Install dependencies (if not installed yet). If you don’t have a `requirements.txt` in this repo yet, install Django directly:

```bash
python -m pip install --upgrade pip
python -m pip install "Django>=5.2,<6"
```

Run migrations and start the server:

```bash
python manage.py migrate
python manage.py runserver
```

Open:

- **Admin**: `http://127.0.0.1:8000/admin/`

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

At the moment, the only URL configured in `config/urls.py` is:

- `/admin/`

There are no app views, templates, or APIs wired up yet (`employees/views.py` is still the default stub).

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
- **App URLs + CRUD**: add `employees/urls.py` and wire it into `config/urls.py`
- **APIs (optional)**: add DRF CRUD endpoints for integrations/automation
- **Validation & constraints**: salary rules, country normalization, etc.
- **Auth & permissions**: restrict HR actions to authorized users
- **Docs**: see `context_skills.md` for a capability/skills checklist