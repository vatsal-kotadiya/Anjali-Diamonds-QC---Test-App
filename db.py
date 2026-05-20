"""SQLite database layer for the Diamond QC app."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

DB_PATH = Path(__file__).parent / "diamond_qc.db"
AUDIO_DIR = Path(__file__).parent / "storage" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS processes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    order_index INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_code TEXT UNIQUE,            -- e.g. vaw03010001 = factory+floor+table+count
    factory_code TEXT,               -- 3-letter factory code (e.g. 'vaw')
    floor TEXT,                      -- 2-digit floor number
    table_no TEXT,                   -- 2-digit table number
    seq_count INTEGER,               -- 4-digit sequence within that factory/floor/table
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin','management','worker')),
    department_id INTEGER,
    process_id INTEGER,              -- worker's fixed process/workstation (NULL for admin/management)
    mobile TEXT,
    address TEXT,
    language_pref TEXT DEFAULT 'en' CHECK (language_pref IN ('en','gu')),
    status TEXT DEFAULT 'active' CHECK (status IN ('active','inactive')),
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (department_id) REFERENCES departments(id),
    FOREIGN KEY (process_id) REFERENCES processes(id)
);

CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id INTEGER NOT NULL,         -- FK to users(id), MUST have role='worker'
    process_id INTEGER NOT NULL,
    diamond_id TEXT NOT NULL,
    report_type TEXT NOT NULL CHECK (report_type IN ('receive','problem')),
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (worker_id) REFERENCES users(id),
    FOREIGN KEY (process_id) REFERENCES processes(id)
);
CREATE INDEX IF NOT EXISTS idx_reports_diamond ON reports(diamond_id);
CREATE INDEX IF NOT EXISTS idx_reports_created ON reports(created_at);

-- Enforce: only users with role='worker' can be the author of a report
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

CREATE TABLE IF NOT EXISTS audio_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL UNIQUE,
    file_uuid TEXT NOT NULL,
    file_path TEXT NOT NULL,
    language TEXT DEFAULT 'gu-IN',
    transcript_original TEXT,
    transcript_english TEXT,
    duration_seconds REAL,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE
);

-- Admin-entered daily counts: how many diamonds each process actually
-- finished on a given date. Used as the denominator for the dashboard's
-- defect-rate bars (defects ÷ total processed = % defective).
CREATE TABLE IF NOT EXISTS process_daily_totals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    process_id INTEGER NOT NULL,
    date TEXT NOT NULL,                  -- ISO date 'YYYY-MM-DD'
    total_diamonds INTEGER NOT NULL CHECK (total_diamonds >= 0),
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE (process_id, date),
    FOREIGN KEY (process_id) REFERENCES processes(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_pdt_date ON process_daily_totals(date);

CREATE TABLE IF NOT EXISTS ai_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL UNIQUE,
    severity TEXT CHECK (severity IN ('Severe','Moderate','Low')),
    root_cause TEXT,
    defect_type TEXT,
    linked_report_id INTEGER,
    correlation_confidence REAL,
    raw_response TEXT,
    responsible_user_id INTEGER,         -- worker Gemini blames for the defect (chain analysis)
    responsibility_reason TEXT,          -- 1-2 sentences explaining the attribution
    chain_summary TEXT,                  -- Gemini's plain-English narrative of the diamond's full chain
    has_matching_problem_report TEXT,    -- 'yes' if any 'problem' report exists for this diamond_id, else 'no'
    stories_consistent TEXT,             -- 'yes' | 'no' | 'unverifiable' (do receive & problem reports describe the same defect?)
    consistency_reason TEXT,             -- 1-line Gemini explanation of the verdict
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE,
    FOREIGN KEY (linked_report_id) REFERENCES reports(id),
    FOREIGN KEY (responsible_user_id) REFERENCES users(id)
);
"""


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    # timeout=10 → if the DB is briefly locked (e.g. DB Browser writing),
    # wait up to 10 seconds before giving up instead of failing immediately.
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        # busy_timeout MUST be set before journal_mode, so the WAL switch
        # itself can wait for any lingering external lock.
        conn.execute("PRAGMA busy_timeout = 10000;")
        # WAL mode lets readers + writers operate in parallel. If another
        # process (DB Browser etc.) holds the lock, skip silently — the
        # connection still works in the existing journal mode.
        try:
            conn.execute("PRAGMA journal_mode = WAL;")
        except sqlite3.OperationalError:
            pass
    except sqlite3.OperationalError:
        pass
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with connect() as c:
        # Run migrations first so the schema script can safely (re)create
        # triggers that reference renamed columns.
        _migrate(c)
        c.executescript(SCHEMA)


def _migrate(c) -> None:
    """Idempotent column additions / renames for existing DBs.

    Runs BEFORE the schema script, so it can rename columns without tripping
    over triggers that reference the new names.
    """
    # reports.user_id -> reports.worker_id (only meaningful for existing DBs)
    rep_info = list(c.execute("PRAGMA table_info(reports)"))
    if rep_info:
        rep_cols = {row["name"] for row in rep_info}
        if "user_id" in rep_cols and "worker_id" not in rep_cols:
            # Drop any stale triggers that might reference the new column name
            for t in ("trg_reports_worker_only_ins", "trg_reports_worker_only_upd"):
                c.execute(f"DROP TRIGGER IF EXISTS {t}")
            c.execute("ALTER TABLE reports RENAME COLUMN user_id TO worker_id")

    # users: add process_id column (each worker bound to one process)
    user_info = list(c.execute("PRAGMA table_info(users)"))
    if user_info:
        ucols = {row["name"] for row in user_info}
        if "process_id" not in ucols:
            c.execute(
                "ALTER TABLE users ADD COLUMN process_id INTEGER REFERENCES processes(id)"
            )

    # ai_analysis: add new chain-analysis columns
    ai_info = list(c.execute("PRAGMA table_info(ai_analysis)"))
    if ai_info:
        existing = {row["name"] for row in ai_info}
        for col, ddl in (
            ("responsible_user_id", "INTEGER REFERENCES users(id)"),
            ("responsibility_reason", "TEXT"),
            ("chain_summary", "TEXT"),
            ("has_matching_problem_report", "INTEGER"),
            ("stories_consistent", "TEXT"),
            ("consistency_reason", "TEXT"),
        ):
            if col not in existing:
                c.execute(f"ALTER TABLE ai_analysis ADD COLUMN {col} {ddl}")


def query_all(sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    with connect() as c:
        return list(c.execute(sql, params))


def query_one(sql: str, params: tuple = ()) -> sqlite3.Row | None:
    with connect() as c:
        return c.execute(sql, params).fetchone()


def execute(sql: str, params: tuple = ()) -> int:
    """Execute and return lastrowid."""
    with connect() as c:
        cur = c.execute(sql, params)
        return cur.lastrowid


def next_emp_code(factory_code: str, floor: str, table_no: str) -> tuple[str, int]:
    """Compute next sequence number for (factory, floor, table) and return (emp_code, seq).

    Format: <factory_3>{floor:02}{table:02}{seq:04}, e.g. vaw03010001.
    """
    factory_code = factory_code.strip().lower()[:3].ljust(3, "x")
    floor_s = str(floor).zfill(2)[:2]
    table_s = str(table_no).zfill(2)[:2]
    row = query_one(
        """SELECT COALESCE(MAX(seq_count), 0) AS m FROM users
           WHERE factory_code = ? AND floor = ? AND table_no = ?""",
        (factory_code, floor_s, table_s),
    )
    next_seq = (row["m"] if row else 0) + 1
    emp_code = f"{factory_code}{floor_s}{table_s}{next_seq:04d}"
    return emp_code, next_seq
