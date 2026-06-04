# sanginiela

Family World Cup pool. Pre-registered players log in with just their email
(no password), predict group-stage scores, and on submit receive an Excel of
their picks by email. Django server-rendered (no DRF), DTL templates + vanilla
JS. See `README.md` for full setup.

## Commands

The project venv lives at `D:\env\quiniela` (interpreter:
`D:\env\quiniela\Scripts\python.exe`).

- `python manage.py runserver` — local dev server (http://localhost:8000/)
- `python manage.py check` — validate models/URLs/imports without a DB
- `python manage.py load_teams` / `load_matches` — seed from `db/jsons/`
- `python manage.py preregister <email> "<name>"` — add a player
- DB selection is env-driven: set `POSTGRES_DB` for Postgres, leave it empty
  to fall back to SQLite at `db/app.sqlite3`.

## Architecture

- Single app `quiniela/`; project package `config/`.
- Views split by concern in `quiniela/views/`: `auth.py` (email login),
  `groups.py` (predictions page), `predictions.py` (JSON save/submit).
- Custom user + domain models in `quiniela/models.py`
  (User, Team, Match, Prediction).
- Excel generation + email in `quiniela/services/excel.py`.
- Data seeding via management commands reading `db/jsons/{teams,matches}.json`.

## Gotchas

- **No passwords.** Login is email-only (`views/auth.py`); `is_active=False`
  means pre-registered but not yet entered. The custom `UserManager` calls
  `set_unusable_password()`.
- **`username` always equals `email`** (forced in `User.save()`). The player's
  display name lives in `first_name`, not `username`.
- **`matches.json` mixes two date formats** (with and without a comma).
  `load_matches` tries both — don't assume a single `strptime` format.
- **`submit_predictions` persists first, then builds the Excel**, so the file
  reflects what was sent. Keep that order.
- **JSON endpoints use a trailing slash** and require the `X-CSRFToken` header
  (set in `static/submit.js`).

## Deploy

Targets AWS (EC2 + RDS Postgres). Production reads `POSTGRES_*` from the
environment; local dev with no `POSTGRES_DB` uses SQLite. Run
`collectstatic` before serving in production.
