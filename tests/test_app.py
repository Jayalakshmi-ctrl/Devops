import pytest
from app import create_app

@pytest.fixture
def app():
    """Create and configure a new app instance for each test case."""
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    
    # Other setup (like initializing a test database) goes here
    yield app
    # Clean up operations go here

@pytest.fixture
def client(app):
    """A test client for the application. Used to make requests."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the application's CLI commands."""
    return app.test_cli_runner()

def test_homepage(client):
    """Test that the home route loads successfully and returns HTTP 200."""
    response = client.get('/')
    assert response.status_code == 200

def test_invalid_route(client):
    """Test that a non-existent page returns a 404 error."""
    response = client.get('/this-page-does-not-exist')
    assert response.status_code == 404

