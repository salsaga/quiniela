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
- Seed (in order; each depends on the prior — `tournament` app):
  `load_stadiums` → `load_stages` → `load_teams` → `load_matches`,
  reading from `db/jsons/{of,fd,manual}/`.
- `python manage.py preregister <email> "<name>"` — add a player (`pool` app)
- `python manage.py simulate` — LOCAL ONLY: shifts the calendar so today is
  matchday 3, fabricates results/predictions/sent states (idempotent; back up
  `db/app.sqlite3` first; restore by re-running the seeds).
- `python manage.py test pool` — unit tests (scoring + leaderboard).
- DB selection is env-driven: set `POSTGRES_DB` for Postgres, leave it empty
  to fall back to SQLite at `db/app.sqlite3`.

## Architecture

- Two apps; project package `config/`. Dependency is one-way: `pool` imports
  from `tournament`, never the reverse.
- `tournament/`: sports data models (`Stadium`, `Stage`, `Team`, `Match`).
- `pool/`: `User` (custom, `AUTH_USER_MODEL = "pool.User"`), `Prediction`,
  `StageUser`.
- Views split by concern in `pool/views/`: `auth.py` (email login),
  `stages.py` (per-stage predictions page + tabs), `predictions.py` (JSON
  save + per-match autosave + send), `leaderboard.py` (standings) and
  `matches.py` (by-day "en juego" view).
- Excel generation + email in `pool/services/excel.py`. Scoring rules in
  `pool/services/scoring.py` (`score_detail`: points + exact/diff flags);
  standings in `pool/services/leaderboard.py` (in-memory, FINISHED only).
  The header rank-chip comes from `pool.context_processors.standing`.
- **No frontend framework** (decided): server-rendered DTL + vanilla JS.
  Future phase simulator should embed data via `json_script` + pure-JS
  module (instant, no server round-trip). If JS rendering ever gets
  unwieldy, the next step is Alpine.js/htmx (no build step), not a SPA.
- Data seeded from two sources committed under `db/jsons/`: OF (openfootball,
  base seed) and FD (football-data.org, `fd_id` + results). Manual overrides
  (e.g. Spanish names) in `db/jsons/manual/`; old files in `db/jsons/legacy/`.

## Gotchas

- **This app is mobile first** Things should look good in a Galaxy S8, 
  try to be responsive, but avoid adding complexity for desktop.
- **`username` always equals `email`** (forced in `User.save()`). The player's
  display name lives in `first_name`, not `username`.
- **`home`/`away`, not `a`/`b`.** Models, templates and `static/submit.js` all
  use `home_team`/`away_team`, `home_goals`/`away_goals`, aligned with FD.
- **Per-stage flow.** Predictions are scoped to a `Stage` (tabs at
  `/stage/<key>/`). Sending is single and final. `StageUser.state` is a
  computed lifecycle (`upcoming`→`editing`→`sent`, plus `locked`) derived from
  `sent_at`, `Stage.opens_at` and `Stage.send_deadline`. A stage is editable
  only once `opens_at` is set and reached (null = not yet enabled).
  `send_expired_stages` (cron, pending on EC2) auto-sends whatever was saved
  for stages past their deadline (skips users who saved nothing).
- **`Match.datetime` is UTC**; local stadium time derives from
  `Stadium.utc_offset` (int). Group/`Stage` is derived on Match, not stored;
  `group_name` lives only on `Team` (CHOICES A–L).
- **OF↔FD team join is by code** (`fifa_code` == `tla`), with one override
  `URU`→`URY` (Uruguay). Match join is by (UTC datetime + home `tla`).
- **`Stage` has 6 rows, not 7**: FD `THIRD_PLACE`+`FINAL` collapse into `FINAL`;
  distinguish via `Match.of_number` (103 = third place, 104 = final). Note the
  ES false friend: `LAST_32` = "dieciseisavos", `LAST_16` = "octavos". OF omits
  `num` for group matches **and** for third place/final, so group detection keys
  off the round (`Matchday*`), never `num` presence.
- **Per-match autosave.** Scores save on `change` via `save_prediction`
  (`/prediction/<id>/`), not a bulk submit. A `Prediction` row exists only when
  both goals are set — an incomplete match deletes its row. Completeness and
  the `N/total` counters derive from row presence, not form state.
- **`send` finalizes what's already in the DB**: it doesn't re-persist the
  client payload, just sets `sent_at`, then builds the Excel. Keep that order
  so the file matches what was sent.
- **JSON endpoints use a trailing slash** and require the `X-CSRFToken` header
  (set in `static/submit.js`).
- **Scoring rules.** `score_detail()` returns `ScoreDetail(points, exact,
  diff_bonus)` or `None` (missing data ≠ 0 pts). Rules: 3 pts for correct
  result; +1 for correct goal difference (non-draws only); +1 for exact
  scoreline. Max: 5 (winner exact) / 4 (draw exact). `exact` and `diff_bonus`
  are disjoint flags.
- **`annotate_result(match, prediction)`** attaches in memory: `is_finished`,
  `user_points`, `diff_bonus`, `base_points`, `points_kind`. `base_points` =
  points − diff_bonus (diff_bonus renders as a separate "+1" badge, so
  displaying `base_points` + badge avoids reading "5+1"). `points_kind` ∈
  {`miss`, `hit`, `exact`} drives CSS color classes (red / green / gold).
- **`tabs_context(user)`** is the standard helper for all views: returns `tabs`
  + `live_after_key` (stage key of the next upcoming match, used to position
  the "en juego" chip). Never call `_build_tabs()` directly.
- **Rival predictions are private until deadline.** `matches_by_day` only
  exposes other players' picks for stages where `Stage.is_past_deadline`.

## Deploy

Targets AWS (EC2 + RDS Postgres). Production reads `POSTGRES_*` from the
environment; local dev with no `POSTGRES_DB` uses SQLite. Run
`collectstatic` before serving in production.
