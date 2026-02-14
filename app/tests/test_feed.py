import pytest

# --- Helper Logic ---

def test_get_feed_authenticated_success(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = client.get("/feed/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_feed_visibility_logic(client, db_session):
    # This test verifies the 'Following' and 'Visibility' rules
    
    # 1. Setup User A (Post Creator)
    client.post("/auth/register", json={"username": "usera", "email": "a@ex.com", "password": "password"})
    login_a = client.post("/auth/login", data={"username": "usera", "password": "password"})
    token_a = login_a.json()["access_token"]
    
    # User A creates a public post and a private post
    client.post("/posts/", data={"content": "Public A", "visibility": "public"}, headers={"Authorization": f"Bearer {token_a}"})
    client.post("/posts/", data={"content": "Private A", "visibility": "private"}, headers={"Authorization": f"Bearer {token_a}"})

    # 2. Setup User B (The Follower)
    client.post("/auth/register", json={"username": "userb", "email": "b@ex.com", "password": "password"})
    login_b = client.post("/auth/login", data={"username": "userb", "password": "password"})
    token_b = login_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 3. User B follows User A
    client.post("/users/usera/follow", headers=headers_b)

    # 4. Action: User B checks their feed
    response = client.get("/feed/", headers=headers_b)
    feed_data = response.json()
    
    # Assertions
    contents = [p["content"] for p in feed_data]
    assert "Public A" in contents
    assert "Private A" not in contents  # Privacy rule check
    assert len(feed_data) == 1

def test_feed_includes_own_posts(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    
    # Create my own private post
    client.post("/posts/", data={"content": "My Secret", "visibility": "private"}, headers=headers)
    
    response = client.get("/feed/", headers=headers)
    contents = [p["content"] for p in response.json()]
    
    # I should be able to see my own private posts in my feed
    assert "My Secret" in contents

def test_feed_pagination(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    # Create 3 posts
    for i in range(3):
        client.post("/posts/", data={"content": f"Post {i}"}, headers=headers)
    
    response = client.get("/feed/?limit=2&page=1", headers=headers)
    assert len(response.json()) == 2