"""Test File for Login Service"""

def user_payload(name="John", email="john@example.com", password="password"):
    """Builder for login accounts object"""
    return {"name": name, "email": email, "password": password}

def test_create_account_ok(client):
    """Tests post method for creating an account"""
    result = client.post("/api/login/sign-up", json=user_payload())
    assert result.status_code == 201
    data = result.json()
    assert data["id"] == 1
    assert data["name"] == "John"
    assert data["email"] == "john@example.com"
    assert data["password"] == "password"

def test_create_account_409(client):
    """Tests 409 on duplicate account creation"""
    client.post("/api/login/sign-up", json=user_payload())
    result = client.post("/api/login/sign-up", json=user_payload())
    assert result.status_code == 409

def test_login_ok(client):
    client.post("/api/login/sign-up", json=user_payload())
    result = client.post("/api/login/sign-in", json={"email": "john@example.com", "password": "password"})
    assert result.status_code == 200

def test_login_inncorect_password(client):
    client.post("/api/login/sign-up", json=user_payload())
    result = client.post("/api/login/sign-in", json={"email": "john@example.com", "password": "passstesttsxujr"})
    assert result.status_code == 400

def test_login_404(client):
    result = client.post("/api/login/sign-in", json={"email": "john@eample.com", "password": "password"})
    assert result.status_code == 404

def test_login_delete_ok(client):
    client.post("/api/login/sign-in", json={"email": "john@eample.com", "password": "password"})
    result = client.delete("/api/login/delete/1")
    assert result.status_code == 204

def test_login_delete_404(client):
    result = client.delete("/api/login/delete/2")
    assert result.status_code == 404

def test_login_get_all_account_when_empty(client):
    result = client.get("/api/login/view")
    assert result.status_code == 200
    data = result.json()
    assert data == []

def test_login_view_account_by_id_ok(client):
    client.post("/api/login/sign-up", json=user_payload())
    result = client.get("/api/login/view/1")
    assert result.status_code == 200
    data = result.json()
    assert data["name"] == "John"
    assert data["password"] == "password"
    assert data["email"] == "john@example.com"

def test_login_view_account_by_id_404(client):
    result = client.get("/api/login/view/2")
    assert result.status_code == 404

def test_login_get_all_account_with_value(client):
    client.post("/api/login/sign-up", json=user_payload())
    result = client.get("/api/login/view")
    assert result.status_code == 200
    data = result.json()
    assert data == [{"id": 1, "name": "John", "email": "john@example.com", "password": "password"}]

def test_login_partial_update_ok(client):
    client.post("/api/login/sign-up", json=user_payload())
    result = client.patch("/api/login/patch/1", json={"password": "password123"})
    assert result.status_code == 200
    data = result.json()
    assert data["password"] == "password123"

def test_login_partial_update_404(client):
    result = client.patch("/api/login/patch/2", json={"password": "password123"})
    assert result.status_code == 404
