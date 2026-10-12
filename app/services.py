import sqlite3
from datetime import datetime

class GymService:
    """Manages persistent SQLite connection pools, client profiles, and progress logs."""
    
    DB_NAME = "aceest_fitness.db"

    PROGRAMS = {
        "Fat Loss (FL)": {"factor": 22},
        "Muscle Gain (MG)": {"factor": 35},
        "Beginner (BG)": {"factor": 26}
    }

    @classmethod
    def _get_db_connection(cls):
        """Creates a thread-safe cursor execution link to the database file backend."""
        conn = sqlite3.connect(cls.DB_NAME)
        # Allows accessing columns by name dict indexes rather than raw tuples
        conn.row_factory = sqlite3.Row
        return conn

    @classmethod
    def init_db(cls):
        """Architects structural entity tables if missing from the runtime instance environment."""
        with cls._get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    age INTEGER,
                    weight REAL,
                    program TEXT,
                    calories INTEGER
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
            conn.commit()

    @classmethod
    def save_client_profile(cls, name, age, weight, program):
        """Calculates energy targets and registers or overrides client records."""
        if not name or not program or program not in cls.PROGRAMS:
            return None

        calories = int(float(weight or 0.0) * cls.PROGRAMS[program]["factor"])

        with cls._get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO clients (name, age, weight, program, calories)
                VALUES (?, ?, ?, ?, ?)
            """, (name, int(age) if age else 0, float(weight) if weight else 0.0, program, calories))
            conn.commit()
            
        return {"name": name, "age": age, "weight": weight, "program": program, "calories": calories}

    @classmethod
    def load_client_profile(cls, name):
        """Fetches distinct relational profile summaries from the database rows."""
        with cls._get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM clients WHERE name=?", (name,))
            row = cur.fetchone()
            
        if not row:
            return None
            
        return {
            "name": row["name"],
            "age": row["age"],
            "weight": row["weight"],
            "program": row["program"],
            "calories": row["calories"]
        }

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
