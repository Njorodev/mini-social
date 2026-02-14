import pytest

# --- Like Logic ---

def test_like_post_success(client, test_user_token):
    # 1. Create a post to like
    headers = {"Authorization": f"Bearer {test_user_token}"}
    post_res = client.post("/posts/", data={"content": "Liking this!"}, headers=headers)
    post_id = post_res.json()["id"]

    # 2. Action: Like the post
    response = client.post(f"/like/{post_id}/like", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Post liked successfully"

def test_like_post_idempotent(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    post_res = client.post("/posts/", data={"content": "Double tap"}, headers=headers)
    post_id = post_res.json()["id"]

    # Like twice
    client.post(f"/like/{post_id}/like", headers=headers)
    response = client.post(f"/like/{post_id}/like", headers=headers)
    
    assert response.status_code == 200
    assert response.json()["message"] == "Post already liked"

def test_like_nonexistent_post(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = client.post("/like/99999/like", headers=headers)
    assert response.status_code == 404

# --- Unlike Logic ---

def test_unlike_post_success(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    post_res = client.post("/posts/", data={"content": "Regret liking this"}, headers=headers)
    post_id = post_res.json()["id"]

    # Like then Unlike
    client.post(f"/like/{post_id}/like", headers=headers)
    response = client.delete(f"/like/{post_id}/like", headers=headers)
    
    assert response.status_code == 200
    assert response.json()["message"] == "Post unliked successfully"

def test_unlike_without_liking(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = client.delete("/like/1/like", headers=headers)
    assert response.status_code == 400
    assert "haven't liked" in response.json()["detail"]

# --- Get Likes ---

def test_get_post_likes_list(client, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    post_res = client.post("/posts/", data={"content": "Popular post"}, headers=headers)
    post_id = post_res.json()["id"]
    
    # Like it
    client.post(f"/like/{post_id}/like", headers=headers)

    response = client.get(f"/like/{post_id}/likes")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    # Check if the list contains the user who liked it
    assert len(response.json()) > 0