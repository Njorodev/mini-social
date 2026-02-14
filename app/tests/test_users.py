import pytest
from app.db.models import User

  # ---List Users---
def test_list_users_admin_success(client, db_session):
    # 1. Register
    client.post("/auth/register", json={
        "username": "admin", "email": "admin@ex.com", "password": "password"
    })

    # 2. MANUALLY update the ROLE field
    admin_user = db_session.query(User).filter(User.username == "admin").first()
    admin_user.role = "admin" 
    
    db_session.commit()
    db_session.close()

    # 3. Login
    login_res = client.post("/auth/login", data={"username": "admin", "password": "password"})
    token = login_res.json()["access_token"]

    # 4. Request
    response = client.get("/users/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
def test_list_users_non_admin_forbidden(client):
    client.post("/auth/register", json={
        "username": "regular", "email": "reg@ex.com", "password": "password"
    })
    login_res = client.post("/auth/login", data={"username": "regular", "password": "password"})
    token = login_res.json()["access_token"]

    response = client.get("/users/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403 

# --- Profile ---
def test_get_profile_exists(client):
    client.post("/auth/register", json={"username": "profile_user", "email": "p@ex.com", "password": "password"})
    # Match router: /users/{username}
    response = client.get("/users/profile_user")
    assert response.status_code == 200

# --- Follow/Unfollow ---
def test_follow_user_flow(client):
    client.post("/auth/register", json={"username": "user1", "email": "u1@ex.com", "password": "password"})
    client.post("/auth/register", json={"username": "user2", "email": "u2@ex.com", "password": "password"})
    login_res = client.post("/auth/login", data={"username": "user1", "password": "password"})
    token = login_res.json()["access_token"]

    # Match router: /users/{username}/follow
    response = client.post("/users/user2/follow", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

def test_unfollow_user_success(client):
    client.post("/auth/register", json={"username": "f1", "email": "f1@ex.com", "password": "password"})
    client.post("/auth/register", json={"username": "f2", "email": "f2@ex.com", "password": "password"})
    login_res = client.post("/auth/login", data={"username": "f1", "password": "password"})
    token = login_res.json()["access_token"]
    
    # Follow first
    client.post("/users/f2/follow", headers={"Authorization": f"Bearer {token}"})

    # Match router: DELETE /users/{username}/unfollow
    response = client.delete("/users/f2/unfollow", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200