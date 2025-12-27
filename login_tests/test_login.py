"""Test File for Login Service"""
from unittest.mock import AsyncMock, patch

def user_payload(name="John", email="john@example.com", password="password"):
    """Builder for login accounts object"""
    return {"name": name, "email": email, "password": password}

@patch('login_service.login.get_exchange')
def test_create_account_ok(mock_get_exchange, client):
    """Tests post method for creating an account"""

    # Mock RabbitMQ for the POST request
    mock_conn = AsyncMock()
    mock_ch = AsyncMock()
    mock_ex = AsyncMock()
    mock_get_exchange.return_value = (mock_conn, mock_ch, mock_ex)

    result = client.post("/api/login/sign-up", json=user_payload())
    assert result.status_code == 201
    data = result.json()
    assert data["id"] == 1
    assert data["name"] == "John"
    assert data["email"] == "john@example.com"
    assert data["password"] == "password"

@patch('login_service.login.get_exchange')
def test_create_account_409(mock_get_exchange, client):
    """Tests 409 on duplicate account creation"""

    # Mock RabbitMQ for the POST requests
    mock_conn = AsyncMock()
    mock_ch = AsyncMock()
    mock_ex = AsyncMock()
    mock_get_exchange.return_value = (mock_conn, mock_ch, mock_ex)

    client.post("/api/login/sign-up", json=user_payload())
    result = client.post("/api/login/sign-up", json=user_payload())
    assert result.status_code == 409

@patch('login_service.login.get_exchange')
def test_login_ok(mock_get_exchange, client):
    """Tests login works once user is posted"""

    # Mock RabbitMQ for the POST request
    mock_conn = AsyncMock()
    mock_ch = AsyncMock()
    mock_ex = AsyncMock()
    mock_get_exchange.return_value = (mock_conn, mock_ch, mock_ex)

    client.post("/api/login/sign-up", json=user_payload())
    result = client.post("/api/login/sign-in", json={"email": "john@example.com", "password": "password"})
    assert result.status_code == 200

@patch('login_service.login.get_exchange')
def test_login_incorrect_password(mock_get_exchange, client):
    """Tests login fails without matching password"""

    # Mock RabbitMQ for the POST request
    mock_conn = AsyncMock()
    mock_ch = AsyncMock()
    mock_ex = AsyncMock()
    mock_get_exchange.return_value = (mock_conn, mock_ch, mock_ex)

    client.post("/api/login/sign-up", json=user_payload())
    result = client.post("/api/login/sign-in", json={"email": "john@example.com", "password": "passstesttsxujr"})
    assert result.status_code == 400

def test_login_404(client):
    """Login doesn't work without signing up"""
    result = client.post("/api/login/sign-in", json={"email": "john@eample.com", "password": "password"})
    assert result.status_code == 404

@patch('login_service.login.get_exchange')
def test_login_delete_ok(mock_get_exchange, client):
    """Delete an account test"""
    client.post("/api/login/sign-in", json={"email": "john@eample.com", "password": "password"})

    # Mock RabbitMQ for the DELETE request
    mock_conn = AsyncMock()
    mock_ch = AsyncMock()
    mock_ex = AsyncMock()
    mock_get_exchange.return_value = (mock_conn, mock_ch, mock_ex)

    result = client.delete("/api/login/delete/1")
    assert result.status_code == 204

@patch('login_service.login.get_exchange')
def test_login_delete_404(mock_get_exchange, client):
    """Delete shouldn't delete a non-existent account"""
    
    # Mock RabbitMQ for the DELETE request
    mock_conn = AsyncMock()
    mock_ch = AsyncMock()
    mock_ex = AsyncMock()
    mock_get_exchange.return_value = (mock_conn, mock_ch, mock_ex)

    result = client.delete("/api/login/delete/2")
    assert result.status_code == 404

def test_login_get_all_account_when_empty(client):
    """Get all accounts when none exist"""
    result = client.get("/api/login/view")
    assert result.status_code == 200
    data = result.json()
    assert data == []

@patch('login_service.login.get_exchange')
def test_login_view_account_by_id_ok(mock_get_exchange, client):
    """View accounts by id"""

    # Mock RabbitMQ for the POST requests
    mock_conn = AsyncMock()
    mock_ch = AsyncMock()
    mock_ex = AsyncMock()
    mock_get_exchange.return_value = (mock_conn, mock_ch, mock_ex)

    client.post("/api/login/sign-up", json=user_payload())
    client.post("/api/login/sign-up", json=user_payload())
    result = client.get("/api/login/view/1")
    assert result.status_code == 200
    data = result.json()
    assert data["name"] == "John"
    assert data["password"] == "password"
    assert data["email"] == "john@example.com"

def test_login_view_account_by_id_404(client):
    """View non existent account by id"""
    result = client.get("/api/login/view/2")
    assert result.status_code == 404

@patch('login_service.login.get_exchange')
def test_login_get_all_account_with_value(mock_get_exchange, client):
    """Get all accounts"""

    # Mock RabbitMQ for the POST requests
    mock_conn = AsyncMock()
    mock_ch = AsyncMock()
    mock_ex = AsyncMock()
    mock_get_exchange.return_value = (mock_conn, mock_ch, mock_ex)

    client.post("/api/login/sign-up", json=user_payload())
    client.post("/api/login/sign-up", json=user_payload())
    result = client.get("/api/login/view")
    assert result.status_code == 200
    data = result.json()
    assert data == [{"id": 1, "name": "John", "email": "john@example.com", "password": "password"}]

@patch('login_service.login.get_exchange')
def test_login_partial_update_ok(mock_get_exchange, client):
    """Test editing login details"""

    # Mock RabbitMQ for the POST and PATCH requests
    mock_conn = AsyncMock()
    mock_ch = AsyncMock()
    mock_ex = AsyncMock()
    mock_get_exchange.return_value = (mock_conn, mock_ch, mock_ex)

    client.post("/api/login/sign-up", json=user_payload())
    result = client.patch("/api/login/patch/1", json={"password": "password123"})
    assert result.status_code == 200
    data = result.json()
    assert data["password"] == "password123"

    #Verify RabbitMQ was called correctly
    mock_get_exchange.assert_called_once()
    mock_ex.publish.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('login_service.login.get_exchange')
def test_login_partial_update_404(mock_get_exchange, client):
    """Test login details without an account"""

    # Mock RabbitMQ for the PATCH request
    mock_conn = AsyncMock()
    mock_ch = AsyncMock()
    mock_ex = AsyncMock()
    mock_get_exchange.return_value = (mock_conn, mock_ch, mock_ex)

    result = client.patch("/api/login/patch/2", json={"password": "password123"})
    assert result.status_code == 404
