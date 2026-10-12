import sqlite3
import io
import base64
from datetime import datetime
import matplotlib
# Prevent matplotlib from attempting to spawn a local window context on headless systems
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class GymService:
    """Manages SQLite persistent data layers, relational joins, and analytics calculations."""
    
    DB_NAME = "aceest_fitness.db"

    # Harmonised dictionary keys to satisfy both manual desktop inputs and test assertions
    PROGRAMS = {
        "Fat Loss (FL)": {"factor": 22, "desc": "Fat loss training block"},
        "Muscle Gain (MG)": {"factor": 35, "desc": "Hypertrophy training block"},
        "Beginner (BG)": {"factor": 26, "desc": "3-day simple beginner full-body"},
        "Fat Loss (FL) – 3 day": {"factor": 22, "desc": "3-day full-body fat loss"},
        "Fat Loss (FL) – 5 day": {"factor": 24, "desc": "5-day split, higher volume fat loss"},
        "Muscle Gain (MG) – PPL": {"factor": 35, "desc": "Push/Pull/Legs hypertrophy split"}
    }

    @classmethod
    def _get_db_connection(cls):
        """Creates a thread-safe connection link to the database backend."""
        conn = sqlite3.connect(cls.DB_NAME)
        conn.row_factory = sqlite3.Row
        return conn

    @classmethod
    def init_db(cls):
        """Architects structural relational tables if missing from the environment."""
        with cls._get_db_connection() as conn:
            cur = conn.cursor()
            
            # Clients core profile master table
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
            
            # Weekly adherence tracking table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_name TEXT,
                    week TEXT,
                    adherence INTEGER
                )
            """)
            
            # Workouts master session logging table
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
            
            # Granular exercises sub-table mapped via foreign identifier keys
            cur.execute("""
                CREATE TABLE IF NOT EXISTS exercises (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workout_id INTEGER,
                    name TEXT,
                    sets INTEGER,
                    reps INTEGER,
                    weight REAL
                )
            """)
            
            # Body weight composition telemetry logger table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_name TEXT,
                    date TEXT,
                    weight REAL,
                    waist REAL,
                    bodyfat REAL
                )
            """)
            conn.commit()

    @classmethod
    def save_client_profile(cls, data):
        """Calculates dynamic metabolic caloric targets and registers client profile logs."""
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
        """Fetches a saved client master record directly out of the database mapping rows."""
        with cls._get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM clients WHERE name=?", (name,))
            row = cur.fetchone()
        if not row:
            return None
        return dict(row)

    @classmethod
    def calculate_bmi_metrics(cls, name):
        """Evaluates clinical BMI values and returns actionable risk categorization data."""
        with cls._get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT height, weight FROM clients WHERE name=?", (name,))
            row = cur.fetchone()
            
        if not row or not row["height"] or not row["weight"]:
            return None

        bmi = row["weight"] / ((row["height"] / 100.0) ** 2)
        bmi = round(bmi, 1)
        
        category = "Normal"
        risk = "Low risk if active and strong."
        if bmi < 18.5:
            category, risk = ("Underweight", "Potential nutrient deficiency.")
        elif bmi >= 30:
            category, risk = ("Obese", "Higher risk; prioritize fat loss tracking.")
        elif bmi >= 25:
            category, risk = ("Overweight", "Moderate risk; focus on consistency.")
            
        return {"bmi": bmi, "category": category, "risk_note": risk}

    @classmethod
    def save_weekly_progress(cls, name, adherence):
        """Generates dynamic chronological week strings and stores adherence data logs."""
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

    @classmethod
    def log_workout_session(cls, name, workout_data, exercise_data):
        """Persists relational workout entities and joins sub-exercises securely across records."""
        with cls._get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO workouts (client_name, date, workout_type, duration_min, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (name, workout_data.get('date'), workout_data.get('type'), 
                  workout_data.get('duration'), workout_data.get('notes')))
            workout_id = cur.lastrowid

            if exercise_data.get('name'):
                cur.execute("""
                    INSERT INTO exercises (workout_id, name, sets, reps, weight)
                    VALUES (?, ?, ?, ?, ?)
                """, (workout_id, exercise_data.get('name'), exercise_data.get('sets'), 
                      exercise_data.get('reps'), exercise_data.get('weight')))
            conn.commit()
        return workout_id
