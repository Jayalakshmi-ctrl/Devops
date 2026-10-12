import sqlite3
import io
import base64
from datetime import datetime
import matplotlib
# Forces Matplotlib to generate image buffers silently without trying to launch a desktop window
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class GymService:
    """Manages SQLite persistent data layers and generates chronological Base64 progress charts."""
    
    DB_NAME = "aceest_fitness.db"

    PROGRAMS = {
        "Fat Loss (FL)": {"factor": 22},
        "Muscle Gain (MG)": {"factor": 35},
        "Beginner (BG)": {"factor": 26}
    }

    @classmethod
    def _get_db_connection(cls):
        conn = sqlite3.connect(cls.DB_NAME)
        conn.row_factory = sqlite3.Row
        return conn

    @classmethod
    def init_db(cls):
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
        with cls._get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM clients WHERE name=?", (name,))
            row = cur.fetchone()
        if not row:
            return None
        return {"name": row["name"], "age": row["age"], "weight": row["weight"], "program": row["program"], "calories": row["calories"]}

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

    @classmethod
    def generate_progress_chart(cls, name):
        """Queries relational rows chronologically and renders a Base64 progress image string."""
        with cls._get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT week, adherence FROM progress 
                WHERE client_name=? ORDER BY id ASC
            """, (name,))
            rows = cur.fetchall()

        if not rows:
            return None

        weeks = [row["week"] for row in rows]
        adherence = [row["adherence"] for row in rows]

        # Draw line plot
        fig, ax = plt.subplots(figsize=(6, 3.5))
        ax.plot(weeks, adherence, marker="o", color="#d4af37", linewidth=2)
        ax.set_title(f"Weekly Adherence Progress - {name}")
        ax.set_xlabel("Week")
        ax.set_ylabel("Adherence (%)")
        ax.set_ylim(0, 100)
        ax.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Buffer image out as a non-persistent byte stream array
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        chart_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig) # Clear cache canvas memory references explicitly
        return chart_b64
