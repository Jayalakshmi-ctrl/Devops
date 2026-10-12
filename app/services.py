import sqlite3
import io
import base64
from datetime import datetime
import matplotlib
# Force Matplotlib to generate images silently without window engines
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class GymService:
    """Manages transactional database engines, multi-table layouts, and performance scoring."""
    
    DB_NAME = "aceest_fitness.db"

    # Synchronised keys mapping backend structures to testing criteria
    PROGRAMS = {
        "Fat Loss (FL) – 3 day": {"factor": 22, "desc": "3-day full-body fat loss"},
        "Fat Loss (FL) – 5 day": {"factor": 24, "desc": "5-day split, higher volume fat loss"},
        "Muscle Gain (MG) – PPL": {"factor": 35, "desc": "Push/Pull/Legs hypertrophy split"},
        "Beginner (BG)": {"factor": 26, "desc": "3-day simple beginner full-body"}
    }

    @classmethod
    def _get_db_connection(cls):
        """Creates a thread-safe connection mapping rows by dictionary indexes."""
        conn = sqlite3.connect(cls.DB_NAME)
        conn.row_factory = sqlite3.Row
        return conn

    @classmethod
    def init_db(cls):
        """Architects schema rules and triggers automated upgrades if definitions clash."""
        with cls._get_db_connection() as conn:
            cur = conn.cursor()
            
            # Dynamic schema check: Upgrade old table structures instantly if columns mismatch
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clients'")
            if cur.fetchone() is not None:
                cur.execute("PRAGMA table_info(clients)")
                cols = [row[1] for row in cur.fetchall()]
                required = {"id", "name", "age", "height", "weight", "program", "calories", "target_weight", "target_adherence"}
                if not required.issubset(set(cols)):
                    cur.execute("DROP TABLE IF EXISTS clients")

            # 1. Primary clients profile table
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
            
            # 2. Weekly adherence history tracking table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_name TEXT,
                    week TEXT,
                    adherence INTEGER
                )
            """)
            
            # 3. Workouts session logging table
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
            
            # 4. Granular exercise lines linked to workout identifiers
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
            
            # 5. Body composition telemetry metrics tracker table
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
        """Calculates dynamic metabolic indices and upserts client profiles."""
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
        """Compiles unified diagnostic parameters cross-table into a relational matrix."""
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

        return {
            "profile": dict(client) if client else None,
            "progress": {"weeks_logged": total_weeks, "avg_adherence": round(avg_adherence or 0, 1)},
            "last_metrics": dict(last_metric) if last_metric else None
        }

    @classmethod
    def calculate_bmi_info(cls, name):
        """Evaluates clinical body mass indicators and returns actionable risk notes."""
        with cls._get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT height, weight FROM clients WHERE name=?", (name,))
            row = cur.fetchone()
            
        if not row or not row["height"] or not row["weight"] or row["height"] <= 0:
            return None

        bmi = row["weight"] / ((row["height"] / 100.0) ** 2)
        bmi = round(bmi, 1)
        
        category, risk = "Normal", "Low risk if active and strong."
        if bmi < 18.5:
            category, risk = "Underweight", "Potential nutrient deficiency, low energy."
        elif bmi >= 30:
            category, risk = "Obese", "Higher risk; prioritize fat loss, consistency, and supervision."
        elif bmi >= 25:
            category, risk = "Overweight", "Moderate risk; focus on adherence and progressive activity."
            
        return {"bmi": bmi, "category": category, "risk_note": risk}

    @classmethod
    def log_workout_session(cls, name, w_data, e_data):
        """Logs structured sessions and stores matching exercises via relational foreign keys."""
        with cls._get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO workouts (client_name, date, workout_type, duration_min, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (name, w_data.get('date'), w_data.get('type'), w_data.get('duration'), w_data.get('notes')))
            workout_id = cur.lastrowid

            if e_data.get('name'):
                cur.execute("""
                    INSERT INTO exercises (workout_id, name, sets, reps, weight)
                    VALUES (?, ?, ?, ?, ?)
                """, (workout_id, e_data.get('name'), e_data.get('sets'), e_data.get('reps'), e_data.get('weight')))
            conn.commit()
        return workout_id

    @classmethod
    def log_body_metrics(cls, name, data):
        """Appends biometric records to log body weight changes chronologically."""
        with cls._get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO metrics (client_name, date, weight, waist, bodyfat)
                VALUES (?, ?, ?, ?, ?)
            """, (name, data.get('date'), data.get('weight'), data.get('waist'), data.get('bodyfat')))
            conn.commit()
        return True

    @classmethod
    def generate_trend_chart(cls, name, table_target):
        """Renders mathematical progressions chronologically as a non-persistent Base64 string."""
        with cls._get_db_connection() as conn:
            cur = conn.cursor()
            if table_target == "progress":
                cur.execute("SELECT week AS x, adherence AS y FROM progress WHERE client_name=? ORDER BY id ASC", (name,))
                title, ylabel = "Weekly Adherence", "Adherence (%)"
            else:
                cur.execute("SELECT date AS x, weight AS y FROM metrics WHERE client_name=? AND weight IS NOT NULL ORDER BY date ASC", (name,))
                title, ylabel = "Weight Trend", "Weight (kg)"
            rows = cur.fetchall()

        if not rows:
            return None

        x_vals = [r["x"] for r in rows]
        y_vals = [r["y"] for r in rows]

        fig, ax = plt.subplots(figsize=(7, 3.5))
        ax.plot(x_vals, y_vals, marker="o", linewidth=2, color="#d4af37" if table_target == "progress" else "orange")
        ax.set_title(f"{title} – {name}")
        ax.set_ylabel(ylabel)
        ax.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close(fig)
        return b64
