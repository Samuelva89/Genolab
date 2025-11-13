from fastapi.testclient import TestClient

def test_create_user(client: TestClient):
    """
    Test creating a user via the /api/users/ endpoint.
    """
    response = client.post(
        "/api/users/",
        json={"email": "newuser@example.com", "name": "New User"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["name"] == "New User"

def test_read_users(client: TestClient):
    """
    Test reading a list of users.
    """
    # Create a couple of users first
    client.post("/api/users/", json={"email": "user1@example.com", "name": "User One"})
    client.post("/api/users/", json={"email": "user2@example.com", "name": "User Two"})

    response = client.get("/api/users/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    assert "user1@example.com" in [user["email"] for user in data]

def test_read_user(client: TestClient):
    """
    Test reading a single user by ID.
    """
    response = client.post("/api/users/", json={"email": "getme@example.com", "name": "Get Me User"})
    user_id = response.json()["id"]

    response = client.get(f"/api/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "getme@example.com"
    assert data["name"] == "Get Me User"
    assert data["id"] == user_id

def test_update_user(client: TestClient):
    """
    Test updating a user's information.
    """
    response = client.post("/api/users/", json={"email": "toupdate@example.com", "name": "To Update User"})
    user_id = response.json()["id"]

    update_data = {"email": "updated@example.com", "name": "Updated User Name", "is_active": False}
    response = client.put(f"/api/users/{user_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "updated@example.com"
    assert data["name"] == "Updated User Name"
    assert data["is_active"] is False

def test_delete_user(client: TestClient):
    """
    Test deleting a user.
    """
    response = client.post("/api/users/", json={"email": "todelete@example.com", "name": "To Delete User"})
    user_id = response.json()["id"]

    # Delete the user
    delete_response = client.delete(f"/api/users/{user_id}")
    assert delete_response.status_code == 204

    # Verify the user is gone
    get_response = client.get(f"/api/users/{user_id}")
    assert get_response.status_code == 404
