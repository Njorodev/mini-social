import pytest

# --- Create & List ---

def test_create_post_authenticated(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    # Using 'data=' sends it as multipart/form-data
    response = client.post("/posts/", 
        data={"title": "Test Title", "content": "Test Content", "visibility": "public"},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Test Title"

def test_create_post_missing_fields(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    # Content is Form(...), meaning it is REQUIRED. 
    # Title is Form(None), so sending only title would fail.
    response = client.post("/posts/",
        data={"title": "I have no content"}, # Content is missing here
        headers=headers
    )
    assert response.status_code == 422
# --- Read & Pagination ---

def test_list_posts_pagination(client):
    response = client.get("/posts/?limit=5&skip=0")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_post_by_id_not_found(client):
    response = client.get("/posts/99999")
    assert response.status_code == 404

# --- Update & Ownership ---
   #  Patch
def test_update_post_owner_success(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    create_res = client.post("/posts/",
        data={"title": "Original", "content": "Old", "visibility": "public"},
        headers=headers
    )
    post_id = create_res.json()["id"]

    # Changed .put to .patch and json to data
    update_res = client.patch(f"/posts/{post_id}",
        data={"content": "Updated Content"},
        headers=headers
    )
    assert update_res.status_code == 200
    assert update_res.json()["content"] == "Updated Content"

def test_update_post_forbidden_for_non_owner(client, test_user_token, db_session):
    # 1. Create a post as User A
    headers_a = {"Authorization": f"Bearer {test_user_token}"}
    post_id = client.post("/posts/", 
        data={"title": "A's Post", "content": "..", "visibility": "public"},
        headers=headers_a
    ).json()["id"]

    # 2. Register/Login User B
    client.post("/auth/register", json={"username": "user_b", "email": "b@ex.com", "password": "password"})
    login_b = client.post("/auth/login", data={"username": "user_b", "password": "password"})
    token_b = login_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 3. User B tries to update User A's post
    response = client.patch(f"/posts/{post_id}", json={"title": "Hacked"}, headers=headers_b)
    assert response.status_code == 403

# --- Delete ---

def test_delete_post_success(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    create_res = client.post("/posts/", data={"title": "To Delete", "content": ".."}, headers=headers)
    post_id = create_res.json()["id"]

    response = client.delete(f"/posts/{post_id}", headers=headers)
    assert response.status_code == 200 

# --- Comments ---

def test_get_comments_nonexistent_post(client):
    response = client.get("/posts/9999/comments")
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"