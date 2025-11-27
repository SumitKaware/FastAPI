# test_main.py
from fastapi.testclient import TestClient
from main import app
from auth import get_current_user # Import the original dependency

# Create a TestClient instance for the FastAPI application
client = TestClient(app)

# ----------------- 1. Test Unprotected Endpoint -----------------

def test_read_root_succeeds():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Protected API"}

# ----------------- 2. Test Protected Endpoint (Failure) -----------------

def test_read_protected_no_token_fails():
    # Attempt to access without the required 'X-Token' header
    response = client.get("/protected")
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid X-Token header. Unauthorized."

# ----------------- 3. Test Protected Endpoint (Success) -----------------

def test_read_protected_valid_token_succeeds():
    # Pass the secret token in the header
    response = client.get(
        "/protected",
        headers={"X-Token": "super-secret-key"}
    )
    assert response.status_code == 200
    assert response.json()["data"] == "Secret information accessed successfully."

# ----------------- 4. Test Protected Endpoint with Dependency Override -----------------

# Define a MOCK/FAKE dependency to use during testing
async def override_get_current_user():
    """Mock dependency that always succeeds and returns a test user."""
    return {"username": "TEST_MOCK_USER"}

def test_read_protected_with_override():
    # Set the dependency override: replace the real function with the mock function
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    # Test the endpoint—it will now use the mock dependency
    response = client.get("/protected")
    
    # Assert success and check the mock data was returned
    assert response.status_code == 200
    assert response.json()["user"]["username"] == "TEST_MOCK_USER"
    
    # BEST PRACTICE: Clear the override after the test is done
    app.dependency_overrides.clear()