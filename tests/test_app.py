import pytest
from app import create_app
from app.services import GymService

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    GymService.CLIENTS_REGISTRY = [] # Reset database array state fields
    with app.test_client() as client:
        yield client

def test_multi_client_and_graph_analytics(client):
    # 1. Post primary user profile
    p1 = {"name": "UserA", "age": 30, "weight": 70.0, "program": "Fat Loss (FL)", "adherence": 90, "notes": "No limits"}
    res1 = client.post('/api/clients', json=p1)
    assert res1.status_code == 201

    # 2. Post secondary analytics user profile
    p2 = {"name": "UserB", "age": 25, "weight": 80.0, "program": "Muscle Gain (MG)", "adherence": 75, "notes": "Focus form"}
    res2 = client.post('/api/clients', json=p2)
    assert res2.status_code == 201

    # 3. Verify total registry count returns 2 records
    list_res = client.get('/api/clients')
    assert len(list_res.get_json()["clients"]) == 2

    # 4. Assert graph image generation stream returns a valid base64 payload
    chart_res = client.get('/api/clients/chart')
    assert chart_res.status_code == 200
    assert "chart_base64" in chart_res.get_json()

    # 5. Check CSV spreadsheet stream contains valid structural row elements
    csv_res = client.get('/api/clients/export')
    assert csv_res.status_code == 200
    assert b"Name,Age,Weight,Program,Adherence,Notes" in csv_res.data
    assert b"UserA" in csv_res.data
