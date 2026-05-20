"""Demo data seeder — run once to populate the DB with test users and reports.

Usage:
    python seed_demo.py

Safe to re-run: uses INSERT OR IGNORE for users, skips if reports already exist.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta

from db import connect, init_db, query_all


# ── Demo management users ────────────────────────────────────────────────────
MANAGEMENT_USERS = [
    ("Rajiv Mehta",    "ceo_rajiv",    "ceo123",    "CEO"),
    ("Priya Shah",     "cto_priya",    "cto123",    "CTO"),
    ("Anil Verma",     "coo_anil",     "coo123",    "COO"),
    ("Sunita Patel",   "mgr_sunita",   "mgr123",    "Manager"),
    ("Deepak Joshi",   "mgr_deepak",   "mgr123",    "Manager"),
    ("Kavita Rao",     "sup_kavita",   "sup123",    "Supervisor"),
]

# ── Demo workers — (name, username, password, department_name) ────────────────
WORKERS = [
    # Sorting
    ("Ramesh Kumar",    "ramesh_k",   "w123", "Sorting"),
    ("Geeta Nair",      "geeta_n",    "w123", "Sorting"),
    ("Suresh Patel",    "suresh_p",   "w123", "Sorting"),
    # Planning
    ("Meena Desai",     "meena_d",    "w123", "Planning"),
    ("Vijay Sharma",    "vijay_s",    "w123", "Planning"),
    # Sawing
    ("Harish Modi",     "harish_m",   "w123", "Sawing"),
    ("Lata Gupta",      "lata_g",     "w123", "Sawing"),
    ("Prakash Singh",   "prakash_s",  "w123", "Sawing"),
    # Bruting
    ("Anita Yadav",     "anita_y",    "w123", "Bruting"),
    ("Bharat Jain",     "bharat_j",   "w123", "Bruting"),
    # Polishing
    ("Rekha Mishra",    "rekha_m",    "w123", "Polishing"),
    ("Mohan Das",       "mohan_d",    "w123", "Polishing"),
    ("Seema Chopra",    "seema_c",    "w123", "Polishing"),
    # Quality Control
    ("Arun Tiwari",     "arun_t",     "w123", "Quality Control"),
    ("Neha Saxena",     "neha_s",     "w123", "Quality Control"),
]

DIAMOND_IDS = [f"D-{n:05d}" for n in range(1, 21)]  # D-00001 … D-00020

SEVERITIES   = ["Severe", "Moderate", "Low"]
DEFECT_TYPES = ["Surface crack", "Inclusion", "Chipped girdle", "Off-round", "Poor polish", "Misalignment"]
ROOT_CAUSES  = [
    "Blade pressure too high during sawing",
    "Worker fatigue during late shift",
    "Coolant contamination",
    "Wrong grit size on polishing wheel",
    "Rough handling in transfer",
    "Misread planning marks",
]
TRANSCRIPTS_EN = [
    "Diamond received with small crack on the girdle.",
    "Surface shows multiple inclusions near the culet.",
    "Stone chipped during bruting — operator error suspected.",
    "Polishing marks visible under magnification.",
    "Off-round shape detected after planning stage.",
    "Clarity grade mismatch — stone sent back for re-check.",
    "Problem report: scratch visible at table facet.",
    "Received from previous station — minor inclusion noted.",
]


def _random_date(days_back: int = 30) -> str:
    offset = random.randint(0, days_back * 24 * 60)
    dt = datetime.utcnow() - timedelta(minutes=offset)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def seed_demo() -> None:
    init_db()

    with connect() as c:
        # ── Ensure base departments + processes exist ────────────────────────
        for name in ["Sorting", "Planning", "Sawing", "Bruting", "Polishing", "Quality Control"]:
            c.execute("INSERT OR IGNORE INTO departments (name) VALUES (?)", (name,))
        for name, idx in [("4P",1),("Sawing",2),("Bruting",3),("Polishing",4),("Faceting",5),("Final QC",6)]:
            c.execute("INSERT OR IGNORE INTO processes (name, order_index) VALUES (?, ?)", (name, idx))

        # ── Management users ─────────────────────────────────────────────────
        for full_name, username, password, title in MANAGEMENT_USERS:
            c.execute(
                """INSERT OR IGNORE INTO users (username, password, name, role, status)
                   VALUES (?, ?, ?, 'management', 'active')""",
                (username, password, full_name),
            )
        print(f"  [OK] {len(MANAGEMENT_USERS)} management users inserted (or already existed)")

        # ── Workers ──────────────────────────────────────────────────────────
        inserted_workers = 0
        for i, (full_name, username, password, dept_name) in enumerate(WORKERS):
            # dept id
            row = c.execute("SELECT id FROM departments WHERE name = ?", (dept_name,)).fetchone()
            if not row:
                continue
            dept_id = row["id"]

            # pick a process that matches dept loosely (round-robin)
            proc_row = c.execute(
                "SELECT id FROM processes ORDER BY order_index LIMIT 1 OFFSET ?",
                (i % 6,),
            ).fetchone()
            proc_id = proc_row["id"] if proc_row else None

            factory = "vaw"
            floor   = str((i // 4) + 1).zfill(2)
            table   = str((i % 4)  + 1).zfill(2)
            seq     = i + 1
            emp_code = f"{factory}{floor}{table}{seq:04d}"

            c.execute(
                """INSERT OR IGNORE INTO users
                   (emp_code, factory_code, floor, table_no, seq_count,
                    username, password, name, role,
                    department_id, process_id, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'worker', ?, ?, 'active')""",
                (emp_code, factory, floor, table, seq,
                 username, password, full_name,
                 dept_id, proc_id),
            )
            inserted_workers += 1
        print(f"  [OK] {inserted_workers} workers inserted (or already existed)")

        # ── Sample reports + AI analysis ─────────────────────────────────────
        existing = c.execute("SELECT COUNT(*) AS n FROM reports").fetchone()["n"]
        if existing >= 30:
            print(f"  [INFO] {existing} reports already exist -- skipping report seed")
            return

        workers_db = list(c.execute(
            "SELECT id, process_id FROM users WHERE role='worker' AND status='active'"
        ))
        if not workers_db:
            print("  [WARN] No workers found -- skipping report seed")
            return

        report_ids = []
        for _ in range(40):
            w = random.choice(workers_db)
            if not w["process_id"]:
                continue
            diamond_id  = random.choice(DIAMOND_IDS)
            report_type = random.choice(["receive", "problem"])
            created_at  = _random_date(30)

            cur = c.execute(
                """INSERT INTO reports (worker_id, process_id, diamond_id, report_type, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (w["id"], w["process_id"], diamond_id, report_type, created_at),
            )
            report_ids.append((cur.lastrowid, diamond_id))

        print(f"  [OK] {len(report_ids)} reports inserted")

        # ── AI analysis rows ─────────────────────────────────────────────────
        for rid, diamond_id in report_ids:
            c.execute(
                """INSERT OR IGNORE INTO ai_analysis
                   (report_id, severity, root_cause, defect_type,
                    correlation_confidence, raw_response)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    rid,
                    random.choice(SEVERITIES),
                    random.choice(ROOT_CAUSES),
                    random.choice(DEFECT_TYPES),
                    round(random.uniform(0.4, 0.95), 2),
                    "demo_seed",
                ),
            )
        print(f"  [OK] {len(report_ids)} AI-analysis rows inserted")

    print("\nDemo seed complete!")
    print("   Passwords — Management: <username>/ceo123|cto123|coo123|mgr123|sup123")
    print("   Passwords — Workers:    <username>/w123")


if __name__ == "__main__":
    seed_demo()
