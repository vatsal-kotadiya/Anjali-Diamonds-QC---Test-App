"""Seed initial data: a default admin user, sample departments, and processes.

Run once after init_db(). Safe to re-run (uses INSERT OR IGNORE).
"""
from db import connect, init_db


DEFAULT_DEPARTMENTS = [
    "Sorting",
    "Planning",
    "Sawing",
    "Bruting",
    "Polishing",
    "Quality Control",
]

DEFAULT_PROCESSES = [
    ("4P", 1),
    ("Sawing", 2),
    ("Bruting", 3),
    ("Polishing", 4),
    ("Faceting", 5),
    ("Final QC", 6),
]


def seed() -> None:
    init_db()
    with connect() as c:
        for name in DEFAULT_DEPARTMENTS:
            c.execute("INSERT OR IGNORE INTO departments (name) VALUES (?)", (name,))
        for name, idx in DEFAULT_PROCESSES:
            c.execute(
                "INSERT OR IGNORE INTO processes (name, order_index) VALUES (?, ?)",
                (name, idx),
            )
        # Default admin — give it a full emp_code so the user-management table
        # renders consistently (admin appears in the same grid as workers).
        c.execute(
            """INSERT OR IGNORE INTO users
               (emp_code, factory_code, floor, table_no, seq_count,
                username, password, name, role, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "adm00000001", "adm", "00", "00", 1,
                "admin", "admin123", "System Administrator", "admin", "active",
            ),
        )
    print("Seed complete. Login as admin / admin123")


if __name__ == "__main__":
    seed()
