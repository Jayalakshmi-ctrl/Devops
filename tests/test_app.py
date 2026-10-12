import pytest
import os
from app import create_app
from app.services import GymService

@pytest.fixture
def client():
    GymService.DB_NAME = "test_version6_fitness.db"
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
    if os.path.exists("test_version6_fitness.db"):
        os.remove("test_version6_fitness.db")

def test_version6_relational_and_analytics_pipelines(client):
    # 1. Store a full biographical profile block
    p_data = {"name": "Jayalakshmi", "age": 44, "height": 165.0, "weight": 68.0, "program": "Muscle Gain (MG) – PPL"}
    assert client.post('/api/clients', json=p_data).status_code == 201

    # 2. Assert dynamic BMI calculations evaluate correctly
    bmi_res = client.get('/api/clients/Jayalakshmi/bmi')
    assert bmi_res.status_code == 200
    assert bmi_res.get_json()["analytics"]["category"] == "Overweight"

    # 3. Log a detailed relational workout and exercise payload record
    w_payload = {
        "workout": {"date": "2026-10-12", "type": "Strength", "duration": 45, "notes": "Felt strong"},
        "exercise": {"name": "Back Squat", "sets": 4, "reps": 8, "weight": 60.0}
    }
    w_res = client.post('/api/clients/Jayalakshmi/workouts', json=w_payload)
    assert w_res.status_code == 201
    assert "workout_id" in w_res.get_json()
