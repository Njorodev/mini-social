import pytest

# --- Create Comment ---

def test_create_comment_success(client, test_user_token):
    # 1. Create a post to comment on
    headers = {"Authorization": f"Bearer {test_user_token}"}
    post_res = client.post("/posts/", data={"content": "Post for comments"}, headers=headers)
    post_id = post_res.json()["id"]

    # 2. Action: Create comment (Using JSON as per the CommentCreate schema)
    response = client.post(
        f"/posts/{post_id}/comments",
        json={"content": "This is a test comment"},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["content"] == "This is a test comment"

def test_create_comment_nonexistent_post(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = client.post(
        "/posts/99999/comments",
        json={"content": "Ghost comment"},
        headers=headers
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"

# --- List Comments ---

def test_get_comments_empty_list(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    post_res = client.post("/posts/", data={"content": "No comments here"}, headers=headers)
    post_id = post_res.json()["id"]

    response = client.get(f"/posts/{post_id}/comments")
    assert response.status_code == 200
    assert response.json() == []

def test_get_comments_pagination(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    post_res = client.post("/posts/", data={"content": "Pagination test"}, headers=headers)
    post_id = post_res.json()["id"]

    # Create 2 comments
    client.post(f"/posts/{post_id}/comments", json={"content": "C1"}, headers=headers)
    client.post(f"/posts/{post_id}/comments", json={"content": "C2"}, headers=headers)

    response = client.get(f"/posts/{post_id}/comments?limit=1&page=1")
    assert response.status_code == 200
    assert len(response.json()) == 1

# --- Delete Comment ---

def test_delete_comment_owner_success(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    post_res = client.post("/posts/", data={"content": "Delete test"}, headers=headers)
    post_id = post_res.json()["id"]
    
    comment_res = client.post(f"/posts/{post_id}/comments", json={"content": "Bye bye"}, headers=headers)
    comment_id = comment_res.json()["id"]

    response = client.delete(f"/comments/{comment_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Comment deleted"

def test_delete_comment_forbidden_non_owner(client, test_user_token):
    # 1. User A creates a comment
    headers_a = {"Authorization": f"Bearer {test_user_token}"}
    post_res = client.post("/posts/", data={"content": "Protected"}, headers=headers_a)
    post_id = post_res.json()["id"]
    comment_id = client.post(f"/posts/{post_id}/comments", json={"content": "Owner's comment"}, headers=headers_a).json()["id"]

    # 2. User B tries to delete it
    client.post("/auth/register", json={"username": "stranger", "email": "s@ex.com", "password": "password"})
    token_b = client.post("/auth/login", data={"username": "stranger", "password": "password"}).json()["access_token"]
    
    response = client.delete(f"/comments/{comment_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert response.status_code == 403