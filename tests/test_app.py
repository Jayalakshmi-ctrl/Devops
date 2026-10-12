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

def test_database_and_chart_generation_flow(client):
    # 1. Post a new client profile record
    payload = {"name": "Vikas", "age": 29, "weight": 82.0, "program": "Fat Loss (FL)"}
    assert client.post('/api/clients', json=payload).status_code == 201
    
    # 2. Log multiple weeks of progress to construct a plot timeline string safely
    client.post('/api/clients/progress', json={"name": "Vikas", "adherence": 70})
    client.post('/api/clients/progress', json={"name": "Vikas", "adherence": 85})
    
    # 3. Pull the dynamic chart endpoint
    chart_res = client.get('/api/clients/Vikas/chart')
    assert chart_res.status_code == 200
    assert "chart_base64" in chart_res.get_json()
