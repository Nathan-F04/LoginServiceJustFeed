"""Test File for Login Service"""

def user_payload(name="John", email="john@example.com", password="password"):
    """Builder for login accounts object"""
    return {"name": name, "email": email, "password": password}

def test_create_account_ok(mock_rabbitmq, client):
    """Tests post method for creating an account"""

    result = client.post("/api/login/sign-up", json=user_payload())
    assert result.status_code == 201
    data = result.json()
    assert data["id"] == 1
    assert data["name"] == "John"
    assert data["email"] == "john@example.com"
    assert data["password"] == "password"
    mock_rabbitmq.assert_called()

def test_create_account_409(mock_rabbitmq, client):
    """Tests 409 on duplicate account creation"""

    client.post("/api/login/sign-up", json=user_payload())
    result = client.post("/api/login/sign-up", json=user_payload())
    assert result.status_code == 409
    mock_rabbitmq.assert_called()

def test_login_ok(mock_rabbitmq, client):
    """Tests login works once user is posted"""

    client.post("/api/login/sign-up", json=user_payload())
    result = client.post("/api/login/sign-in", json={"email": "john@example.com", "password": "password"})
    assert result.status_code == 200
    mock_rabbitmq.assert_called()

def test_login_incorrect_password(mock_rabbitmq, client):
    """Tests login fails without matching password"""

    client.post("/api/login/sign-up", json=user_payload())
    result = client.post("/api/login/sign-in", json={"email": "john@example.com", "password": "passstesttsxujr"})
    assert result.status_code == 400
    mock_rabbitmq.assert_called()

def test_login_404(client):
    """Login doesn't work without signing up"""
    result = client.post("/api/login/sign-in", json={"email": "john@eample.com", "password": "password"})
    assert result.status_code == 404

def test_login_delete_ok(mock_rabbitmq, client):
    """Delete an account test"""
    client.post("/api/login/sign-up", json=user_payload())

    result = client.delete("/api/login/delete/1")
    assert result.status_code == 204
    mock_rabbitmq.assert_called()

def test_login_delete_404(client):
    """Delete shouldn't delete a non-existent account"""

    result = client.delete("/api/login/delete/2")
    assert result.status_code == 404

def test_login_get_all_account_when_empty(client):
    """Get all accounts when none exist"""
    result = client.get("/api/login/view")
    assert result.status_code == 200
    data = result.json()
    assert data == []

def test_login_view_account_by_id_ok(mock_rabbitmq, client):
    """View accounts by id"""

    client.post("/api/login/sign-up", json=user_payload())
    client.post("/api/login/sign-up", json=user_payload())
    result = client.get("/api/login/view/1")
    assert result.status_code == 200
    data = result.json()
    assert data["name"] == "John"
    assert data["password"] == "password"
    assert data["email"] == "john@example.com"
    mock_rabbitmq.assert_called()

def test_login_view_account_by_id_404(client):
    """View non existent account by id"""
    result = client.get("/api/login/view/2")
    assert result.status_code == 404

def test_login_get_all_account_with_value(mock_rabbitmq, client):
    """Get all accounts"""

    client.post("/api/login/sign-up", json=user_payload())
    client.post("/api/login/sign-up", json=user_payload())
    result = client.get("/api/login/view")
    assert result.status_code == 200
    data = result.json()
    assert data == [{"id": 1, "name": "John", "email": "john@example.com", "password": "password"}]
    mock_rabbitmq.assert_called()

def test_login_partial_update_ok(mock_rabbitmq, client):
    """Test editing login details"""

    client.post("/api/login/sign-up", json=user_payload())
    result = client.patch("/api/login/patch/1", json={"password": "password123"})
    assert result.status_code == 200
    data = result.json()
    assert data["password"] == "password123"

    mock_rabbitmq.assert_called()

def test_login_partial_update_404(client):
    """Test login details without an account"""

    result = client.patch("/api/login/patch/2", json={"password": "password123"})
    assert result.status_code == 404
