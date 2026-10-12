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

    PROGRAMS = {
        "Fat Loss (FL) – 3 day": {"factor": 22, "desc": "3-day full-body fat loss"},
        "Fat Loss (FL) – 5 day": {"factor": 24, "desc": "5-day split, higher volume fat loss"},
        "Muscle Gain (MG) – PPL": {"factor": 35, "desc": "Push/Pull/Legs hypertrophy"},
        "Beginner (BG)": {"factor": 26, "desc": "3-day simple beginner full-body"}
    }

    @classmethod
    def _get_db_connection(cls):
        conn = sqlite3.connect(cls.DB_NAME)
        conn.row_factory = sqlite3.Row
        return conn

    @classmethod
    def init_db(cls):
        """Initializes tables or forces upgrades if old schema formats are detected."""
        with cls._get_db_connection() as conn:
            cur = conn.cursor()
            
            # Step 1: Handle schema check & upgrade migrations safely
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clients'")
            if cur.fetchone() is not None:
                cur.pragma("table_info(clients)")
                cols = [row[1] for row in cur.fetchall()]
                required = {"id", "name", "age", "height", "weight", "program", "calories", "target_weight", "target_adherence"}
                if not required.issubset(set(cols)):
                    cur.execute("DROP TABLE IF EXISTS clients")

            # Step 2: Establish the full Version 6 database tables
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
    def get_client_summary(cls, name):
        """Compiles an aggregate profile tracking report drawing metrics cross-table."""
        with cls._get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM clients WHERE name=?", (name,))
            client = cur.fetchone()
            if not client:
                return None

            cur.execute("SELECT COUNT(*), AVG(adherence) FROM progress WHERE client_name=?", (name,))
            total_weeks, avg_adherence = cur.fetchone()
            
            cur.execute("SELECT * FROM metrics WHERE client_name=? ORDER BY date DESC LIMIT 1", (name,))
            last_metric = cur.fetchone()

        metric_summary = dict(last_metric) if last_metric else None
        return {
            "profile": dict(client),
            "progress": {"weeks_logged": total_weeks, "avg_adherence": round(avg_adherence or 0, 1)},
            "last_metrics": metric_summary
        }

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
        
        category, risk = ("Normal", "Low risk if active.")
        if bmi < 18.5: category, risk = ("Underweight", "Potential nutrient deficiency.")
        elif bmi >= 30: category, risk = ("Obese", "Higher risk; prioritize fat loss.")
        elif bmi >= 25: category, risk = ("Overweight", "Moderate risk; focus on consistency.")
            
        return {"bmi": bmi, "category": category, "risk_note": risk}

    @classmethod
    def log_workout_session(cls, name, workout_data, exercise_data):
        """Persists relational workout entities across distinct join tables."""
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

    @classmethod
    def generate_weight_trend_chart(cls, name):
        """Assembles line graphs detailing body composition variations over time."""
        with cls._get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT date, weight FROM metrics WHERE client_name=? AND weight IS NOT NULL ORDER BY date ASC", (name,))
            rows = cur.fetchall()

        if not rows: return None
        dates, weights = [r["date"] for r in rows], [r["weight"] for r in rows]

        fig, ax = plt.subplots(figsize=(6, 3.5))
        ax.plot(dates, weights, marker="o", linewidth=2, color="orange")
        ax.set_title(f"Weight Trend Timeline – {name}")
        ax.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close(fig)
        return b64
