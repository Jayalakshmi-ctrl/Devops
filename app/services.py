class GymService:
    """Manages core business logic, dynamic calorie tracking, and client logs."""

    # Updated metrics dataset matching the Version 2 Tkinter profile matrix
    PROGRAMS = {
        "Fat Loss (FL)": {
            "workout": "Mon: Back Squat 5x5 + Core\nTue: EMOM 20min Assault Bike\nWed: Bench Press + 21-15-9\nThu: Deadlift + Box Jumps\nFri: Zone 2 Cardio 30min",
            "diet": "Breakfast: Egg Whites + Oats\nLunch: Grilled Chicken + Brown Rice\nDinner: Fish Curry + Millet Roti\nTarget: ~2000 kcal",
            "color": "#e74c3c",
            "calorie_factor": 22
        },
        "Muscle Gain (MG)": {
            "workout": "Mon: Squat 5x5\nTue: Bench 5x5\nWed: Deadlift 4x6\nThu: Front Squat 4x8\nFri: Incline Press 4x10\nSat: Barbell Rows 4x10",
            "diet": "Breakfast: Eggs + Peanut Butter Oats\nLunch: Chicken Biryani\nDinner: Mutton Curry + Rice\nTarget: ~3200 kcal",
            "color": "#2ecc71",
            "calorie_factor": 35
        },
        "Beginner (BG)": {
            "workout": "Full Body Circuit:\n- Air Squats\n- Ring Rows\n- Push-ups\nFocus: Technique & Consistency",
            "diet": "Balanced Tamil Meals\nIdli / Dosa / Rice + Dal\nProtein Target: 120g/day",
            "color": "#3498db",
            "calorie_factor": 26
        }
    }

    # In-memory storage mock simulating database client data tracking
    CLIENTS_DB = {}

    @classmethod
    def get_program_details(cls, name):
        """Retrieves workout charts, configurations, and baseline variables."""
        return cls.PROGRAMS.get(name)

    @classmethod
    def calculate_estimated_calories(cls, program_name, weight):
        """Evaluates dynamic calorie targets using systemic mass factors."""
        program = cls.get_program_details(program_name)
        if not program or not weight or weight <= 0:
            return None
        return int(weight * program["calorie_factor"])

    @classmethod
    def save_client_profile(cls, name, age, weight, program, adherence):
        """Validates incoming client state metrics and persists data models."""
        if not name or not program or program not in cls.PROGRAMS:
            return None
        
        estimated_calories = cls.calculate_estimated_calories(program, weight)
        
        client_data = {
            "name": name,
            "age": int(age) if age else 0,
            "weight": float(weight) if weight else 0.0,
            "program": program,
            "weekly_adherence_percent": int(adherence) if adherence else 0,
            "estimated_calories": estimated_calories
        }
        
        # Persist profile to our simulation data store layer
        cls.CLIENTS_DB[name] = client_data
        return client_data

