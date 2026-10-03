import sqlite3
from pathlib import Path


DB_PATH = Path("data/trials.db")


def get_connection():
    DB_PATH.parent.mkdir(exist_ok=True)

    return sqlite3.connect(DB_PATH)


def create_tables():

    conn = get_connection()

    # Main normalized trial table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS trials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trial_id TEXT,
            crop TEXT,
            product TEXT,
            country TEXT,
            year INTEGER,
            trial_type TEXT,
            treatment_yield_kg_ha REAL,
            control_yield_kg_ha REAL,
            source TEXT,
            source_type TEXT,
            notes TEXT
        )
    """)

    # Every original source associated with a trial
    conn.execute("""
        CREATE TABLE IF NOT EXISTS trial_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trial_id TEXT,
            source TEXT,
            source_type TEXT,
            treatment_yield_kg_ha REAL,
            control_yield_kg_ha REAL,
            notes TEXT
        )
    """)

    conn.commit()
    conn.close()


def clear_database():

    conn = get_connection()

    conn.execute("DELETE FROM trials")
    conn.execute("DELETE FROM trial_sources")

    conn.commit()
    conn.close()


def insert_trial(trial):

    conn = get_connection()

    conn.execute("""
        INSERT INTO trials (
            trial_id,
            crop,
            product,
            country,
            year,
            trial_type,
            treatment_yield_kg_ha,
            control_yield_kg_ha,
            source,
            source_type,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        trial.trial_id,
        trial.crop,
        trial.product,
        trial.country,
        trial.year,
        trial.trial_type,
        trial.treatment_yield_kg_ha,
        trial.control_yield_kg_ha,
        trial.source,
        trial.source_type,
        trial.notes,
    ))

    conn.commit()
    conn.close()


def insert_source(trial):

    conn = get_connection()

    conn.execute("""
        INSERT INTO trial_sources (
            trial_id,
            source,
            source_type,
            treatment_yield_kg_ha,
            control_yield_kg_ha,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        trial.trial_id,
        trial.source,
        trial.source_type,
        trial.treatment_yield_kg_ha,
        trial.control_yield_kg_ha,
        trial.notes,
    ))

    conn.commit()
    conn.close()


def get_all_trials():

    conn = get_connection()

    cursor = conn.execute("""
        SELECT
            trial_id,
            crop,
            product,
            country,
            year,
            trial_type,
            treatment_yield_kg_ha,
            control_yield_kg_ha,
            source,
            source_type,
            notes
        FROM trials
        ORDER BY trial_id
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


def get_sources(trial_id):

    conn = get_connection()

    cursor = conn.execute("""
        SELECT
            trial_id,
            source,
            source_type,
            treatment_yield_kg_ha,
            control_yield_kg_ha,
            notes
        FROM trial_sources
        WHERE trial_id = ?
        ORDER BY source
    """, (trial_id,))

    rows = cursor.fetchall()

    conn.close()

    return rows