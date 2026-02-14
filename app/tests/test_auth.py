import pytest

## --- Registration Tests ---

def test_register_success(client):
    response = client.post("/auth/register", json={
        "username": "testuser", "email": "test@example.com", "password": "password123"
    })
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"

def test_register_duplicate_username(client):
    # First registration
    client.post("/auth/register", json={
        "username": "sameuser", "email": "1@example.com", "password": "password"
    })
    # Duplicate registration
    response = client.post("/auth/register", json={
        "username": "sameuser", "email": "2@example.com", "password": "password"
    })
    assert response.status_code == 400
    assert "Username or email already registered" in response.json()["detail"]

def test_register_invalid_fields(client):
    response = client.post("/auth/register", json={
        "username": "", "email": "not-an-email"
    })
    assert response.status_code == 422  # Unprocessable Entity (Validation Error)

## --- Login & Token Tests ---

def test_login_success(client):
    # Setup: Register a user
    client.post("/auth/register", json={
        "username": "loginuser", "email": "login@example.com", "password": "securepassword"
    })
    # Action: Login
    response = client.post("/auth/login", data={
        "username": "loginuser", "password": "securepassword"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    # return response.json()["access_token"]

def test_login_wrong_credentials(client):
    response = client.post("/auth/login", data={
        "username": "loginuser", "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]

## --- Profile & Protected Routes ---

def test_get_me_success(client):
    # 1. Register & Login to get token
    client.post("/auth/register", json={
        "username": "me", "email": "me@example.com", "password": "password"
    })
    login_res = client.post("/auth/login", data={"username": "me", "password": "password"})
    token = login_res.json()["access_token"]

    # 2. Access protected route
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "me"

def test_get_me_unauthorized(client):
    response = client.get("/auth/me", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401

## --- Refresh & Logout ---

def test_refresh_token_valid(client):
    # 1. Setup User
    client.post("/auth/register", json={
        "username": "refresh_user", "email": "refresh@example.com", "password": "password123"
    })
    
    # 2. Login to get BOTH tokens
    login_res = client.post("/auth/login", data={"username": "refresh_user", "password": "password123"})
    login_data = login_res.json()
    access_token = login_data.get("access_token")
    refresh_token = login_data.get("refresh_token")

    # 3. Call Refresh
    # MUST pass the access_token in headers because of Depends(get_current_user)
    response = client.post(
        "/auth/refresh", 
        json={"refresh_token": refresh_token},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_logout_valid_token(client):
    # 1. Register a fresh user
    client.post("/auth/register", json={
        "username": "logout_user", "email": "logout@example.com", "password": "password123"
    })
    
    # 2. Login to get a valid access token
    login_res = client.post("/auth/login", data={"username": "logout_user", "password": "password123"})
    token = login_res.json().get("access_token")
    
    # 3. Logout
    response = client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200