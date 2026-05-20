# Diamond QC — Full Database Schema

Complete SQLite table structure for the Diamond QC app as it exists in
[db.py](db.py). All tables use `INTEGER PRIMARY KEY AUTOINCREMENT` for `id`
and `TEXT` timestamps defaulted via `(datetime('now'))`.

Tables (in order they appear in the schema):

1. `sessions` — legacy, unused
2. `departments`
3. `processes`
4. `users`
5. `reports`
6. `audio_files`
7. `process_daily_totals`
8. `ai_analysis`

---

## 1. `sessions` (legacy, unused)

Leftover from the original login flow. The app currently uses a persona
selector instead of login, so this table stays empty. Safe to drop later.

| Column       | Type     | Constraints                          |
|--------------|----------|--------------------------------------|
| `token`      | TEXT     | PRIMARY KEY                          |
| `user_id`    | INTEGER  | NOT NULL, FK → `users(id)` ON DELETE CASCADE |
| `created_at` | TEXT     | DEFAULT `(datetime('now'))`          |

```sql
CREATE TABLE IF NOT EXISTS sessions (
  token      TEXT PRIMARY KEY,
  user_id    INTEGER NOT NULL,
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

---

## 2. `departments`

Admin-configurable list of departments (Sorting, Planning, Sawing, Bruting,
Polishing, Quality Control by default).

| Column       | Type     | Constraints                          |
|--------------|----------|--------------------------------------|
| `id`         | INTEGER  | PRIMARY KEY AUTOINCREMENT            |
| `name`       | TEXT     | NOT NULL, UNIQUE                     |
| `created_at` | TEXT     | DEFAULT `(datetime('now'))`          |

```sql
CREATE TABLE IF NOT EXISTS departments (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  name       TEXT NOT NULL UNIQUE,
  created_at TEXT DEFAULT (datetime('now'))
);
```

---

## 3. `processes`

Admin-configurable manufacturing stages (4P, Sawing, Bruting, Polishing,
Faceting, Final QC). `order_index` controls dashboard display order.

| Column        | Type     | Constraints                          |
|---------------|----------|--------------------------------------|
| `id`          | INTEGER  | PRIMARY KEY AUTOINCREMENT            |
| `name`        | TEXT     | NOT NULL, UNIQUE                     |
| `order_index` | INTEGER  | DEFAULT 0                            |
| `created_at`  | TEXT     | DEFAULT `(datetime('now'))`          |

```sql
CREATE TABLE IF NOT EXISTS processes (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  name        TEXT NOT NULL UNIQUE,
  order_index INTEGER DEFAULT 0,
  created_at  TEXT DEFAULT (datetime('now'))
);
```

---

## 4. `users`

Single table for admin, management, and workers. `emp_code` is the human-
readable factory code (`vaw03010001`). Workers must also have `process_id`
set so reports auto-attach to their workstation.

| Column          | Type     | Constraints                                                            | Notes                                          |
|-----------------|----------|------------------------------------------------------------------------|------------------------------------------------|
| `id`            | INTEGER  | PRIMARY KEY AUTOINCREMENT                                              | Internal ID, used by FKs                       |
| `emp_code`      | TEXT     | UNIQUE                                                                 | e.g. `vaw03010001`                             |
| `factory_code`  | TEXT     |                                                                        | 3-letter factory code                          |
| `floor`         | TEXT     |                                                                        | 2-digit floor                                  |
| `table_no`      | TEXT     |                                                                        | 2-digit table                                  |
| `seq_count`     | INTEGER  |                                                                        | 4-digit sequence within (factory, floor, table)|
| `username`      | TEXT     | NOT NULL, UNIQUE                                                       | Login                                          |
| `password`      | TEXT     | NOT NULL                                                               | Plaintext (MVP only)                           |
| `name`          | TEXT     | NOT NULL                                                               | Full name                                      |
| `role`          | TEXT     | NOT NULL, CHECK (role IN ('admin','management','worker'))              |                                                |
| `department_id` | INTEGER  | FK → `departments(id)`                                                 | Nullable                                       |
| `process_id`    | INTEGER  | FK → `processes(id)`                                                   | Required for workers; NULL for admin/management|
| `mobile`        | TEXT     |                                                                        |                                                |
| `address`       | TEXT     |                                                                        |                                                |
| `language_pref` | TEXT     | DEFAULT 'en', CHECK (language_pref IN ('en','gu'))                     | Worker UI language                             |
| `status`        | TEXT     | DEFAULT 'active', CHECK (status IN ('active','inactive'))              |                                                |
| `created_at`    | TEXT     | DEFAULT `(datetime('now'))`                                            |                                                |

```sql
CREATE TABLE IF NOT EXISTS users (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  emp_code      TEXT UNIQUE,
  factory_code  TEXT,
  floor         TEXT,
  table_no      TEXT,
  seq_count     INTEGER,
  username      TEXT NOT NULL UNIQUE,
  password      TEXT NOT NULL,
  name          TEXT NOT NULL,
  role          TEXT NOT NULL CHECK (role IN ('admin','management','worker')),
  department_id INTEGER,
  process_id    INTEGER,
  mobile        TEXT,
  address       TEXT,
  language_pref TEXT DEFAULT 'en' CHECK (language_pref IN ('en','gu')),
  status        TEXT DEFAULT 'active' CHECK (status IN ('active','inactive')),
  created_at    TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (department_id) REFERENCES departments(id),
  FOREIGN KEY (process_id)    REFERENCES processes(id)
);
```

---

## 5. `reports`

One row per audio submission by a worker. `worker_id` is enforced at the
trigger level to point only at users with `role = 'worker'`.

| Column        | Type     | Constraints                                                       |
|---------------|----------|-------------------------------------------------------------------|
| `id`          | INTEGER  | PRIMARY KEY AUTOINCREMENT                                         |
| `worker_id`   | INTEGER  | NOT NULL, FK → `users(id)`; **must reference role='worker'** (trigger) |
| `process_id`  | INTEGER  | NOT NULL, FK → `processes(id)`                                    |
| `diamond_id`  | TEXT     | NOT NULL                                                          |
| `report_type` | TEXT     | NOT NULL, CHECK (report_type IN ('receive','problem'))            |
| `created_at`  | TEXT     | DEFAULT `(datetime('now'))`                                       |

```sql
CREATE TABLE IF NOT EXISTS reports (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  worker_id   INTEGER NOT NULL,
  process_id  INTEGER NOT NULL,
  diamond_id  TEXT NOT NULL,
  report_type TEXT NOT NULL CHECK (report_type IN ('receive','problem')),
  created_at  TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (worker_id)  REFERENCES users(id),
  FOREIGN KEY (process_id) REFERENCES processes(id)
);

CREATE INDEX IF NOT EXISTS idx_reports_diamond ON reports(diamond_id);
CREATE INDEX IF NOT EXISTS idx_reports_created ON reports(created_at);

-- Enforce worker_id MUST reference a user whose role = 'worker'
CREATE TRIGGER IF NOT EXISTS trg_reports_worker_only_ins
BEFORE INSERT ON reports
FOR EACH ROW
WHEN (SELECT role FROM users WHERE id = NEW.worker_id) != 'worker'
BEGIN
  SELECT RAISE(ABORT, 'reports.worker_id must reference a user with role=worker');
END;

CREATE TRIGGER IF NOT EXISTS trg_reports_worker_only_upd
BEFORE UPDATE OF worker_id ON reports
FOR EACH ROW
WHEN (SELECT role FROM users WHERE id = NEW.worker_id) != 'worker'
BEGIN
  SELECT RAISE(ABORT, 'reports.worker_id must reference a user with role=worker');
END;
```

---

## 6. `audio_files`

Stores transcription + path. Actual audio bytes live on disk in
`./storage/audio/<file_uuid>.webm` (or `.wav` from older recorder). One audio
per report.

| Column                | Type     | Constraints                                                |
|-----------------------|----------|------------------------------------------------------------|
| `id`                  | INTEGER  | PRIMARY KEY AUTOINCREMENT                                  |
| `report_id`           | INTEGER  | NOT NULL, UNIQUE, FK → `reports(id)` ON DELETE CASCADE     |
| `file_uuid`           | TEXT     | NOT NULL                                                   |
| `file_path`           | TEXT     | NOT NULL                                                   |
| `language`            | TEXT     | DEFAULT 'gu-IN'                                            |
| `transcript_original` | TEXT     | Sarvam STT output (Gujarati)                               |
| `transcript_english`  | TEXT     | Sarvam translate → Gemini refine                           |
| `duration_seconds`    | REAL     |                                                            |
| `created_at`          | TEXT     | DEFAULT `(datetime('now'))`                                |

```sql
CREATE TABLE IF NOT EXISTS audio_files (
  id                  INTEGER PRIMARY KEY AUTOINCREMENT,
  report_id           INTEGER NOT NULL UNIQUE,
  file_uuid           TEXT NOT NULL,
  file_path           TEXT NOT NULL,
  language            TEXT DEFAULT 'gu-IN',
  transcript_original TEXT,
  transcript_english  TEXT,
  duration_seconds    REAL,
  created_at          TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE
);
```

---

## 7. `process_daily_totals`

Admin-entered daily counts: how many diamonds each process actually finished
on a given date. Used as the denominator for the dashboard's defect-rate
bars (defects ÷ total processed × 100 = % defective).

| Column           | Type     | Constraints                                                     |
|------------------|----------|-----------------------------------------------------------------|
| `id`             | INTEGER  | PRIMARY KEY AUTOINCREMENT                                       |
| `process_id`     | INTEGER  | NOT NULL, FK → `processes(id)` ON DELETE CASCADE                |
| `date`           | TEXT     | NOT NULL, ISO date `YYYY-MM-DD`                                 |
| `total_diamonds` | INTEGER  | NOT NULL, CHECK (`total_diamonds >= 0`)                         |
| `created_at`     | TEXT     | DEFAULT `(datetime('now'))`                                     |
| —                | —        | UNIQUE (`process_id`, `date`) — one row per process per day     |

```sql
CREATE TABLE IF NOT EXISTS process_daily_totals (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  process_id     INTEGER NOT NULL,
  date           TEXT NOT NULL,
  total_diamonds INTEGER NOT NULL CHECK (total_diamonds >= 0),
  created_at     TEXT DEFAULT (datetime('now')),
  UNIQUE (process_id, date),
  FOREIGN KEY (process_id) REFERENCES processes(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_pdt_date ON process_daily_totals(date);
```

---

## 8. `ai_analysis`

Gemini's analysis per report: severity, defect type, root cause, correlation
link, **responsibility assignment** (which worker caused the defect, when the
diamond has 2+ reports), and a flag for whether any matching 'problem' report
exists for the same diamond.

| Column                        | Type     | Constraints                                                  | Notes                                                       |
|-------------------------------|----------|--------------------------------------------------------------|-------------------------------------------------------------|
| `id`                          | INTEGER  | PRIMARY KEY AUTOINCREMENT                                    |                                                             |
| `report_id`                   | INTEGER  | NOT NULL, UNIQUE, FK → `reports(id)` ON DELETE CASCADE       | 1:1 with report                                             |
| `severity`                    | TEXT     | CHECK (severity IN ('Severe','Moderate','Low'))              | Nullable until Gemini completes                             |
| `root_cause`                  | TEXT     |                                                              | Plain-English root cause                                    |
| `defect_type`                 | TEXT     |                                                              | e.g. crack, chip, burn                                      |
| `linked_report_id`            | INTEGER  | FK → `reports(id)`                                           | Earlier report Gemini matched (same diamond / defect)       |
| `correlation_confidence`      | REAL     |                                                              | 0.0–1.0                                                     |
| `raw_response`                | TEXT     |                                                              | Full Gemini JSON for debugging                              |
| `responsible_user_id`         | INTEGER  | FK → `users(id)`                                             | Chain analysis result — who Gemini blames                   |
| `responsibility_reason`       | TEXT     |                                                              | 1–2 sentence explanation                                    |
| `chain_summary`               | TEXT     |                                                              | Plain-English narrative across the chain                    |
| `has_matching_problem_report` | TEXT     |                                                              | `'yes'` if any 'problem' report exists for the same diamond, else `'no'` |
| `stories_consistent`          | TEXT     |                                                              | `'yes'` / `'no'` / `'unverifiable'` — do receive & problem reports describe the same defect? |
| `consistency_reason`          | TEXT     |                                                              | 1-line Gemini explanation of the `stories_consistent` verdict |
| `created_at`                  | TEXT     | DEFAULT `(datetime('now'))`                                  |                                                             |

```sql
CREATE TABLE IF NOT EXISTS ai_analysis (
  id                          INTEGER PRIMARY KEY AUTOINCREMENT,
  report_id                   INTEGER NOT NULL UNIQUE,
  severity                    TEXT CHECK (severity IN ('Severe','Moderate','Low')),
  root_cause                  TEXT,
  defect_type                 TEXT,
  linked_report_id            INTEGER,
  correlation_confidence      REAL,
  raw_response                TEXT,
  responsible_user_id         INTEGER,
  responsibility_reason       TEXT,
  chain_summary               TEXT,
  has_matching_problem_report TEXT,
  stories_consistent          TEXT,
  consistency_reason          TEXT,
  created_at                  TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (report_id)           REFERENCES reports(id) ON DELETE CASCADE,
  FOREIGN KEY (linked_report_id)    REFERENCES reports(id),
  FOREIGN KEY (responsible_user_id) REFERENCES users(id)
);
```

---

## Relationships (ER summary)

```
departments 1───* users               (department_id)
processes   1───* users               (process_id — workers only)
processes   1───* reports             (process_id)
users       1───* reports             (worker_id, trigger-enforced role='worker')
users       1───* ai_analysis         (responsible_user_id)
reports     1───1 audio_files
reports     1───1 ai_analysis
reports     1───* ai_analysis         (via linked_report_id — self-correlation)
processes   1───* process_daily_totals
users       1───* sessions            (legacy, unused)
```

---

## Cascade / Delete behaviour

| When you delete...   | What happens                                                                          |
|----------------------|---------------------------------------------------------------------------------------|
| A `department`       | `users.department_id` becomes orphaned (no ON DELETE clause — SQLite leaves it dangling unless `foreign_keys = ON` rejects the delete) |
| A `process`          | Cascades to `process_daily_totals` rows for that process                              |
| A `user` (worker)    | Cascades to `sessions`. Reports stay (FK doesn't cascade), so deleting a worker who has reports requires you to delete reports first if `foreign_keys = ON` |
| A `report`           | Cascades to `audio_files` + `ai_analysis`                                             |

---

## PRAGMAs (set on every connection — see `db.connect()` in [db.py](db.py))

```sql
PRAGMA foreign_keys = ON;      -- enforce FK constraints
PRAGMA busy_timeout = 10000;   -- wait up to 10s for a lock
PRAGMA journal_mode = WAL;     -- readers + writer in parallel (silently skipped if locked)
```

---

## Default seed data

When [seed.py](seed.py) runs:

- 6 **departments**: Sorting, Planning, Sawing, Bruting, Polishing, Quality Control
- 6 **processes** (with order_index): 4P, Sawing, Bruting, Polishing, Faceting, Final QC
- 1 **admin user**: `admin / admin123` (emp_code `adm00000001`)
