class GymService:
    """Manages core business logic and fitness plans for ACEest Fitness & Gym."""
    
    # Core fitness data extracted from the initial Tinker dashboard asset
    PROGRAMS = {
        "Fat Loss (FL)": {
            "workout": "Mon: 5x5 Back Squat + AMRAP\nTue: EMOM 20min Assault Bike\nWed: Bench Press + 21-15-9\nThu: 10RFT Deadlifts/Box Jumps\nFri: 30min Active Recovery",
            "diet": "B: 3 Egg Whites + Oats Idli\nL: Grilled Chicken + Brown Rice\nD: Fish Curry + Millet Roti\nTarget: 2,000 kcal",
            "color": "#e74c3c"
        },
        "Muscle Gain (MG)": {
            "workout": "Mon: Squat 5x5\nTue: Bench 5x5\nWed: Deadlift 4x6\nThu: Front Squat 4x8\nFri: Incline Press 4x10\nSat: Barbell Rows 4x10",
            "diet": "B: 4 Eggs + PB Oats\nL: Chicken Biryani (250g Chicken)\nD: Mutton Curry + Jeera Rice\nTarget: 3,200 kcal",
            "color": "#2ecc71"
        },
        "Beginner (BG)": {
            "workout": "Circuit Training: Air Squats, Ring Rows, Push-ups.\nFocus: Technique Mastery & Form (90% Threshold)",
            "diet": "Balanced Tamil Meals: Idli-Sambar, Rice-Dal, Chapati.\nProtein: 120g/day",
            "color": "#3498db"
        }
    }

    @staticmethod
    def get_welcome_message():
        """Returns standard system status and site metadata summary."""
        return {
            "status": "success",
            "message": "Welcome to ACEest FUNCTIONAL FITNESS API",
            "metrics": {
                "capacity": "150 Users",
                "area": "10,000 sq ft",
                "break_even": "250 Members"
            }
        }

    @classmethod
    def get_all_programs(cls):
        """Returns a list of all available programmatic plan names."""
        return list(cls.PROGRAMS.keys())

    @classmethod
    def get_program_details(cls, program_name):
        """Fetches workout plans, target dietary details, and configurations for a key."""
        return cls.PROGRAMS.get(program_name)
