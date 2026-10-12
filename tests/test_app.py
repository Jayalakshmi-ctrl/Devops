import pytest
import os
from app import create_app
from app.services import GymService

@pytest.fixture
def client():
    GymService.DB_NAME = "test_aceest_fitness.db"
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
    if os.path.exists("test_aceest_fitness.db"):
        os.remove("test_aceest_fitness.db")

def test_database_persistence_and_loading(client):
    payload = {"name": "Arun", "age": 28, "weight": 75.0, "program": "Muscle Gain (MG)"}
    res_post = client.post('/api/clients', json=payload)
    assert res_post.status_code == 201
    
    res_get = client.get('/api/clients/Arun')
    assert res_get.status_code == 200
    data = res_get.get_json()["client_profile"]
    assert data["calories"] == 2625  # 75.0 * 35

def test_weekly_progress_logging(client):
    progress_payload = {"name": "Arun", "adherence": 85}
    res = client.post('/api/clients/progress', json=progress_payload)
    assert res.status_code == 201
    assert "Week" in res.get_json()["progress_log"]["week"]
