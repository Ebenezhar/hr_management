# Project Context + Skills (`hr_management`)

This document is a **context brief** for the codebase and a **skills/capability checklist** for implementing the necessary HR management functionality in a clean, incremental way.

## Current state (facts from repo)

- **Framework**: Django 5.2 (generated with 5.2.13)
- **Apps**:
  - `employees` (installed in `config/settings.py`)
- **Database**: SQLite (`db.sqlite3`)
- **URLs**: only Django admin is routed (`/admin/`)
- **Domain model**: `employees.models.EmployeeRecord`
  - `full_name`, `job_title`, `country`, `salary`
- **Migrations**:
  - `0001_initial`: created model as `Employee`
  - `0002_rename_employee_employeerecord`: renamed to `EmployeeRecord`
- **Known gap**: `employees/tests.py` references the old model name and won’t run as-is

## Product intent (what this should become)

An HR management system typically grows in layers:

- **Employee master data**: create/update/terminate employees, search/filter
- **HR operations**: salary history, department, manager, employment status, documents
- **Governance**: authentication, authorization, audit trail, data export
- **Delivery**: admin-first and/or API-first (REST) backend

This repo is currently at **“model exists”** stage.

## “Skills” checklist (capabilities needed)

Think of these as the *skills the codebase should gain* (or the implementation work to add) to reach a minimal viable HR system.

## Active Implementation

### 3) CRUD skill (employees module)

Status:
- **API-first implementation** is in progress using **Django REST Framework (DRF)**
- **Endpoints being developed**: `GET` (List) and `POST` (Create) for **`/api/employees/`**
- **Testing skill initiated (RED phase)**: tests are currently **failing** for these endpoints (expected while implementation is underway)

### 1) Django fundamentals (project hygiene)

- **Environment skill**: predictable dev setup (`.venv`, dependency pinning, run instructions)
- **Settings skill**: separate dev/prod settings (at minimum: `DEBUG`, `ALLOWED_HOSTS`, secret key via env)
- **Database skill**: migrations are the source of truth (avoid editing `db.sqlite3` manually)

Deliverables (typical):
- `requirements.txt` (or `pyproject.toml`)
- `.env.example` + `django-environ` (optional but common)

### 2) Admin skill (HR back office quickly)

The fastest usable UI in Django is the admin.

Needed:
- **Model registration**: register `EmployeeRecord` in `employees/admin.py`
- **Admin UX**: list display, search fields, filters, ordering
- **Data integrity**: field validation, constraints

### 4) URL routing skill (public app entrypoints)

Needed:
- `employees/urls.py`
- include app routes from `config/urls.py`
- predictable naming (`employees:list`, `employees:create`, etc.)

### 5) Validation & domain rules skill

Typical HR rules to encode:
- **Salary**: non-negative, currency strategy, max digits/precision
- **Country**: normalized list (ISO codes) or free text (current is free text)
- **Name**: basic normalization and length constraints

### 6) Security & permissions skill

At minimum:
- **Authentication**: Django auth
- **Authorization**: staff-only or group-based permissions for HR actions
- **CSRF**: default Django protections (already present via middleware)
- **Secrets**: remove hard-coded `SECRET_KEY` from source for production usage

### 7) Testing skill

Needed:
- **Fix broken starter test**: align tests with `EmployeeRecord`
- **Model tests**: creation, validations, string representation
- **View/API tests**: CRUD flows, permission checks

### 8) Data lifecycle skill

Real HR systems rarely hard-delete people.

Options:
- **Soft delete / archive** (e.g., `is_active`, `terminated_at`)
- **History tracking** (salary changes over time)
- **Audit log** (who changed what, when)

### 9) Reporting/export skill (often requested early)

Common deliverables:
- **CSV export** for employee list
- **Basic summary reports** (headcount by country/job title, salary totals)

## Suggested “MVP” scope for this repo

If the goal is a clean first usable version, a good MVP is:

- Admin UI for `EmployeeRecord` (search, list, edit)
- DRF CRUD endpoints (optional, for integrations)
- Working tests for model + at least one view/API endpoint
- Clean setup docs and dependency file

## Operational notes

- This repo currently has **no dependency file** checked in (no `requirements.txt`). If you want reproducible installs, add one.
- `db.sqlite3` is present. For teams, it’s usually better to ignore it and rely on migrations.

## Glossary

- **Skill (in this document)**: a capability the project should support (feature, module, or engineering practice).
- **EmployeeRecord**: the current core data model representing an employee entry.
