import io
import base64
import csv
import matplotlib
# Prevent matplotlib from trying to open a desktop GUI window in the background
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class GymService:
    """Manages multi-client data registries, calorie engines, and analytical reporting models."""

    PROGRAMS = {
        "Fat Loss (FL)": {"workout": "Back Squat, Cardio, Bench, Deadlift, Recovery",
                          "diet": "Egg Whites, Chicken, Fish Curry",
                          "color": "#e74c3c", "calorie_factor": 22},
        "Muscle Gain (MG)": {"workout": "Squat, Bench, Deadlift, Press, Rows",
                             "diet": "Eggs, Biryani, Mutton Curry",
                             "color": "#2ecc71", "calorie_factor": 35},
        "Beginner (BG)": {"workout": "Air Squats, Ring Rows, Push-ups",
                          "diet": "Balanced Tamil Meals",
                          "color": "#3498db", "calorie_factor": 26}
    }

    # Internal list database simulating multi-client tracking
    CLIENTS_REGISTRY = []

    @classmethod
    def get_program_details(cls, name):
        return cls.PROGRAMS.get(name)

    @classmethod
    def calculate_calories(cls, program_name, weight):
        program = cls.get_program_details(program_name)
        if not program or not weight or weight <= 0:
            return None
        return int(weight * program["calorie_factor"])

    @classmethod
    def save_client(cls, name, age, weight, program, adherence, notes):
        """Appends a new client profile payload onto the systemic tracking engine."""
        if not name or not program or program not in cls.PROGRAMS:
            return None
            
        estimated_calories = cls.calculate_calories(program, weight)
        client_profile = {
            "name": name,
            "age": int(age) if age else 0,
            "weight": float(weight) if weight else 0.0,
            "program": program,
            "adherence": int(adherence) if adherence else 0,
            "notes": str(notes) if notes else "",
            "estimated_calories": estimated_calories
        }
        cls.CLIENTS_REGISTRY.append(client_profile)
        return client_profile

    @classmethod
    def get_all_clients(cls):
        return cls.CLIENTS_REGISTRY

    @classmethod
    def generate_progress_chart(cls):
        """Assembles a Matplotlib bar graph and renders it as an exportable Base64 image payload."""
        if not cls.CLIENTS_REGISTRY:
            return None
            
        names = [c["name"] for c in cls.CLIENTS_REGISTRY]
        adherence = [c["adherence"] for c in cls.CLIENTS_REGISTRY]
        
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.bar(names, adherence, color="#d4af37")
        ax.set_ylabel("Adherence %")
        ax.set_title("Client Progress Tracker")
        plt.tight_layout()
        
        # Buffer and stream binary image payload straight out without disk footprints
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)
        base64_str = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        plt.close(fig) # Flush engine context
        return base64_str

    @classmethod
    def generate_csv_data(cls):
        """Compiles rows of client records inside memory buffers for file export streams."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Name", "Age", "Weight", "Program", "Adherence", "Notes"])
        
        for c in cls.CLIENTS_REGISTRY:
            writer.writerow([c["name"], c["age"], c["weight"], c["program"], c["adherence"], c["notes"]])
            
        return output.getvalue()
