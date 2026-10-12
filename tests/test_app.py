import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_dynamic_calorie_injection(client):
    """Ensures dynamic parameters properly process calorie equations."""
    # Weight: 80kg * Muscle Gain factor (35) = 2800 kcal
    response = client.get('/api/programs/Muscle Gain (MG)?weight=80')
    assert response.status_code == 200
    data = response.get_json()
    assert data["estimated_calories"] == 2800

def test_successful_client_creation_payload(client):
    """Validates full persistence loops via structured POST requests."""
    payload = {
        "name": "Jayalakshmi",
        "age": 44,
        "weight": 65.0,
        "program": "Fat Loss (FL)",
        "adherence": 85
    }
    response = client.post('/api/clients', json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert "saved successfully" in data["message"]
    assert data["client_profile"]["estimated_calories"] == 1430  # 65 * 22

def test_client_creation_validation_fault(client):
    """Verifies error responses for missing parameters."""
    incomplete_payload = {"name": "TestUser"}  # Missing operational program parameter
    response = client.post('/api/clients', json=incomplete_payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "Missing required details" in data["message"]

