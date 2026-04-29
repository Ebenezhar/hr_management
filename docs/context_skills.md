# Project Context + Skills (`hr_management`)

This document is a **context brief** for the codebase and a **skills/capability checklist** for implementing the necessary HR management functionality in a clean, incremental way.

## Current state (facts from repo)

- **Framework**: Django 5.2 (generated with 5.2.13)
- **Apps**:
  - `employees` (installed in `config/settings.py`)
- **Database**: SQLite (`db.sqlite3`)
- **API**: Django REST Framework (DRF) is in use (`rest_framework.views.APIView`, `rest_framework.response.Response`)
- **URLs**:
  - Django admin is routed at `/admin/`
  - API is routed at `/api/` via `config/urls.py` → `include("employees.urls")`
- **Domain model**: `employees.models.EmployeeRecord`
  - `full_name`, `job_title`, `country`, `salary`
- **Migrations**:
  - `0001_initial`: created model as `Employee`
  - `0002_rename_employee_employeerecord`: renamed to `EmployeeRecord`
- **Known gap**: `employees/tests.py` references the old model name and won’t run as-is

## Current API surface (implemented)

All endpoints below are prefixed with `/api/` (see `config/urls.py`).

### Employee CRUD

- `GET /api/employees/`
  - Lists all `EmployeeRecord` rows
- `POST /api/employees/`
  - Creates a new `EmployeeRecord`
  - Validates via `employees.serializers.EmployeeSerializer`:
    - name/job title/country regex + length constraints
    - salary must be a valid Decimal and **> 0**
    - country must be one of `employees.config.ACCEPTED_COUNTRIES`

### Salary calculation (tax deduction)

- `GET /api/employees/<employee_id>/salary-details/`
  - Returns employee identity fields plus computed salary details from `employees.core_logic.EmployeeTaxDeductionCalculator`:
    - `salary` (2dp)
    - `tax_rate` (2dp)
    - `tax_deduction` (2dp)
    - `net_salary` (2dp)
  - Uses `employees.config.EMPLOYEE_TAX_RATES` and Decimal rounding (no floats)

### Aggregation / metrics

- `GET /api/employees/metrics/country/<country>/`
  - Filters employees by `country__iexact`
  - Returns:
    - `min_salary`, `max_salary`, `avg_salary` (2dp)
    - `country_tax_rate` (2dp, derived from configured tax table when country matches)
    - `avg_salary_after_tax` (2dp; tax applied to computed average for determinism)
- `GET /api/employees/metrics/job-title/<title>/`
  - Filters employees by `job_title__iexact`
  - Returns:
    - `avg_salary` (2dp)

## Product intent (what this should become)

An HR management system typically grows in layers:

- **Employee master data**: create/update/terminate employees, search/filter
- **HR operations**: salary history, department, manager, employment status, documents
- **Governance**: authentication, authorization, audit trail, data export
- **Delivery**: admin-first and/or API-first (REST) backend

This repo is currently at **“API foundation exists”** stage (model + DRF endpoints + validation + some reporting/metrics).

## “Skills” checklist (capabilities needed)

Think of these as the *skills the codebase should gain* (or the implementation work to add) to reach a minimal viable HR system.

## Active Implementation

### 3) CRUD skill (employees module)

Status:
- **API-first implementation** exists using **Django REST Framework (DRF)** with `APIView`
- **CRUD endpoints implemented**:
  - `GET /api/employees/` (list)
  - `POST /api/employees/` (create)
- **Validation is implemented** in `EmployeeSerializer` (format rules + accepted countries + Decimal salary)

### 3a) Salary calculation skill (tax deduction)

Status:
- **Employee salary details API implemented**:
  - `GET /api/employees/<employee_id>/salary-details/`
- **Calculation logic implemented** in `employees/core_logic.py`:
  - Decimal-only math with rounding to 2dp
  - tax rate lookup via `employees/config.py` (`EMPLOYEE_TAX_RATES`)

### 3b) Metrics/reporting skill (aggregations)

Status:
- **Country salary metrics API implemented**:
  - `GET /api/employees/metrics/country/<country>/` (min/max/avg + tax on avg)
- **Job title salary metrics API implemented**:
  - `GET /api/employees/metrics/job-title/<title>/` (avg)

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

Status:
- `employees/urls.py` exists
- app routes are included from `config/urls.py` under `/api/`
- predictable route naming exists for most endpoints (e.g. `employee-list-create`, `employee-salary-details`, metrics names)

### 5) Validation & domain rules skill

Typical HR rules to encode:
- **Salary**: positive Decimal (current API requires **> 0**), currency strategy, max digits/precision
- **Country**: accepted choice list (current API validates against `ACCEPTED_COUNTRIES`)
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
