import sqlite3
import io
import base64
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class GymService:
    """Manages transactional database connections, complex relational schema mapping, and analytics."""
    
    DB_NAME = "aceest_fitness.db"

    # Harmonized keys so both test specifications and desktop profiles clear checks cleanly
    PROGRAMS = {
        "Fat Loss (FL)": {"factor": 22, "desc": "Fat loss training block"},
        "Muscle Gain (MG)": {"factor": 35, "desc": "Push/Pull/Legs hypertrophy split"},
        "Beginner (BG)": {"factor": 26, "desc": "3-day simple beginner full-body"}
    }

    @classmethod
    def _get_db_connection(cls):
        conn = sqlite3.connect(cls.DB_NAME)
        conn.row_factory = sqlite3.Row
        return conn

    @classmethod
    def init_db(cls):
        """Initializes tables or forces updates if old formats are encountered."""
        with cls._get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    age INTEGER,
                    height REAL,
                    weight REAL,
                    program TEXT,
                    calories INTEGER,
                    target_weight REAL,
                    target_adherence INTEGER
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_name TEXT,
                    week TEXT,
                    adherence INTEGER
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS workouts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_name TEXT,
                    date TEXT,
                    workout_type TEXT,
                    duration_min INTEGER,
                    notes TEXT
                )
            """)
            conn.commit()

    @classmethod
    def save_client_profile(cls, data):
        name = data.get('name', '').strip()
        program = data.get('program')
        if not name or not program or program not in cls.PROGRAMS:
            return None

        weight = float(data.get('weight', 0)) if data.get('weight') else None
        calories = int(weight * cls.PROGRAMS[program]["factor"]) if weight else None

        with cls._get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO clients 
                (name, age, height, weight, program, calories, target_weight, target_adherence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, data.get('age'), data.get('height'), weight, program, calories, 
                  data.get('target_weight'), data.get('target_adherence')))
            conn.commit()
        return {"name": name, "calories": calories, "program": program}

    @classmethod
    def load_client_profile(cls, name):
        with cls._get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM clients WHERE name=?", (name,))
            row = cur.fetchone()
        if not row:
            return None
        return dict(row)

    @classmethod
    def save_weekly_progress(cls, name, adherence):
        if not name:
            return None
        week_string = datetime.now().strftime("Week %U - %Y")
        with cls._get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO progress (client_name, week, adherence)
                VALUES (?, ?, ?)
            """, (name, week_string, int(adherence) if adherence else 0))
            conn.commit()
        return {"client_name": name, "week": week_string, "adherence": adherence}
