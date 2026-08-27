"""
models.py
Everything related to talking to the SQLite database lives here:
connecting, creating tables, seeding starter data, and the small
helper functions routes.py calls to read/write records.
"""
import sqlite3
from datetime import datetime

from flask import current_app, g


# ---------------------------------------------------------------------------
# Connection handling
# ---------------------------------------------------------------------------

def get_db_connection():
    """Return a SQLite connection, reusing one per request via Flask's `g`."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


# ---------------------------------------------------------------------------
# Schema + seed data
# ---------------------------------------------------------------------------

def init_db(app):
    """Create tables (if needed) and seed starter insurance/emergency data."""
    with app.app_context():
        db = get_db_connection()

        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS pets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                animal TEXT NOT NULL,
                age TEXT,
                allergies TEXT,
                owner TEXT,
                image_file TEXT
            );

            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER NOT NULL,
                report_name TEXT NOT NULL,
                report_file TEXT NOT NULL,
                date_uploaded TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pet_id) REFERENCES pets (id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                virtual INTEGER DEFAULT 0,
                FOREIGN KEY (pet_id) REFERENCES pets (id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS emergency_contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT,
                type TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS insurance_policy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                coverage TEXT NOT NULL,
                premium REAL NOT NULL,
                benefits TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS pet_insurance (
                pet_id INTEGER NOT NULL,
                policy_id INTEGER NOT NULL,
                PRIMARY KEY (pet_id, policy_id),
                FOREIGN KEY (pet_id) REFERENCES pets (id) ON DELETE CASCADE,
                FOREIGN KEY (policy_id) REFERENCES insurance_policy (id) ON DELETE CASCADE
            );
            """
        )
        db.commit()

        # Seed insurance policies only if the table is empty
        existing = db.execute("SELECT COUNT(*) AS c FROM insurance_policy").fetchone()["c"]
        if existing == 0:
            policies = [
                ("Basic Plan", "Basic coverage for accidents and illnesses.",
                 "Accidents, Illnesses", 1500, "Coverage up to ₹50,000 per incident, 80% reimbursement after ₹1000 deductible."),
                ("Premium Plan", "Comprehensive coverage with additional benefits.",
                 "Accidents, Illnesses, Wellness", 2500, "Coverage up to ₹1,00,000 per incident, 90% reimbursement after ₹500 deductible, annual wellness exam."),
                ("Ultimate Plan", "All-inclusive coverage with maximum benefits.",
                 "Accidents, Illnesses, Wellness, Surgery", 3500, "Unlimited incident coverage, 100% reimbursement after ₹0 deductible, annual wellness exam, surgery covered."),
                ("Standard Plan", "Standard coverage for common pet health issues.",
                 "Common illnesses, Minor injuries", 2000, "Coverage up to ₹70,000 per incident, 85% reimbursement after ₹750 deductible."),
                ("Family Plan", "Coverage for multiple pets in one household.",
                 "Accidents, Illnesses, Routine care", 5000, "Coverage up to ₹2,00,000 per incident, 80% reimbursement after ₹1500 deductible, covers up to 3 pets."),
                ("Wellness Plan", "Focuses on preventative care and routine check-ups.",
                 "Routine check-ups, Vaccinations, Wellness exams", 1000, "Coverage up to ₹20,000 per year, 100% reimbursement after ₹200 deductible."),
            ]
            db.executemany(
                "INSERT INTO insurance_policy (name, description, coverage, premium, benefits) "
                "VALUES (?, ?, ?, ?, ?)",
                policies,
            )

        existing = db.execute("SELECT COUNT(*) AS c FROM emergency_contacts").fetchone()["c"]
        if existing == 0:
            contacts = [
                ("Jeeva Pet Hospital", "080 3580 1887", "Kanakapura Rd, Bengaluru", "24/7 Animal Hospital"),
                ("i-Vet Pet Hospital & Pet Store", "080 884 60247", "Vasanthapura Main Rd, Bengaluru", "Veterinarian"),
                ("Friendly Tails Pet Hospital", "096114 60533", "Bengaluru", "Hospital"),
                ("New Pets Vet Clinic", "080 4112 3456", "14th Main Rd, Bengaluru", "Veterinary Care"),
            ]
            db.executemany(
                "INSERT INTO emergency_contacts (name, phone, address, type) VALUES (?, ?, ?, ?)",
                contacts,
            )

        db.commit()


# ---------------------------------------------------------------------------
# Pets
# ---------------------------------------------------------------------------

def fetch_all_pets():
    db = get_db_connection()
    return db.execute("SELECT * FROM pets ORDER BY id DESC").fetchall()


def fetch_pet(pet_id):
    db = get_db_connection()
    return db.execute("SELECT * FROM pets WHERE id = ?", (pet_id,)).fetchone()


def add_pet(name, animal, age, allergies, owner, image_file):
    db = get_db_connection()
    db.execute(
        "INSERT INTO pets (name, animal, age, allergies, owner, image_file) VALUES (?, ?, ?, ?, ?, ?)",
        (name, animal, age, allergies, owner, image_file),
    )
    db.commit()


def update_pet(pet_id, name, animal, age, allergies, owner, image_file=None):
    db = get_db_connection()
    if image_file:
        db.execute(
            "UPDATE pets SET name=?, animal=?, age=?, allergies=?, owner=?, image_file=? WHERE id=?",
            (name, animal, age, allergies, owner, image_file, pet_id),
        )
    else:
        db.execute(
            "UPDATE pets SET name=?, animal=?, age=?, allergies=?, owner=? WHERE id=?",
            (name, animal, age, allergies, owner, pet_id),
        )
    db.commit()


def delete_pet(pet_id):
    db = get_db_connection()
    db.execute("DELETE FROM pets WHERE id = ?", (pet_id,))
    db.commit()


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

def fetch_all_reports():
    db = get_db_connection()
    return db.execute("SELECT * FROM reports ORDER BY date_uploaded DESC").fetchall()


def add_report(pet_id, report_name, report_file):
    db = get_db_connection()
    db.execute(
        "INSERT INTO reports (pet_id, report_name, report_file, date_uploaded) VALUES (?, ?, ?, ?)",
        (pet_id, report_name, report_file, datetime.utcnow().isoformat(timespec="seconds")),
    )
    db.commit()


# ---------------------------------------------------------------------------
# Appointments
# ---------------------------------------------------------------------------

def fetch_all_appointments():
    db = get_db_connection()
    return db.execute(
        """
        SELECT appointments.*, pets.name AS pet_name
        FROM appointments
        JOIN pets ON pets.id = appointments.pet_id
        ORDER BY date ASC
        """
    ).fetchall()


def add_appointment(pet_id, date, description, virtual):
    db = get_db_connection()
    db.execute(
        "INSERT INTO appointments (pet_id, date, description, virtual) VALUES (?, ?, ?, ?)",
        (pet_id, date, description, 1 if virtual else 0),
    )
    db.commit()


# ---------------------------------------------------------------------------
# Emergency contacts
# ---------------------------------------------------------------------------

def fetch_emergency_contacts():
    db = get_db_connection()
    return db.execute("SELECT * FROM emergency_contacts ORDER BY name ASC").fetchall()


# ---------------------------------------------------------------------------
# Insurance
# ---------------------------------------------------------------------------

def fetch_all_policies():
    db = get_db_connection()
    return db.execute("SELECT * FROM insurance_policy ORDER BY premium ASC").fetchall()


def fetch_pet_policies(pet_id):
    db = get_db_connection()
    return db.execute(
        """
        SELECT insurance_policy.*
        FROM insurance_policy
        JOIN pet_insurance ON insurance_policy.id = pet_insurance.policy_id
        WHERE pet_insurance.pet_id = ?
        """,
        (pet_id,),
    ).fetchall()


def fetch_pet_insurance():
    """All pet <-> policy links, used to annotate the pet dashboard."""
    db = get_db_connection()
    return db.execute("SELECT * FROM pet_insurance").fetchall()


def add_pet_policy(pet_id, policy_id):
    db = get_db_connection()
    db.execute(
        "INSERT OR IGNORE INTO pet_insurance (pet_id, policy_id) VALUES (?, ?)",
        (pet_id, policy_id),
    )
    db.commit()
