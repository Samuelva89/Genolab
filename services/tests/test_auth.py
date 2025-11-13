from fastapi.testclient import TestClient

def test_register_new_user(client: TestClient):
    """
    Test successful user registration.
    """
    response = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "name": "Test User"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
    assert "id" in data
    assert "is_active" in data
    assert "is_admin" in data
    assert data["is_admin"] is False  # Ensure new users are not admins

def test_register_existing_user(client: TestClient):
    """
    Test registration with an email that already exists.
    """
    # First, create a user
    client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "name": "Test User"},
    )
    
    # Then, try to create it again
    response = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "name": "Another Test User"}, # Name can be different
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "El email ya está registrado."}
