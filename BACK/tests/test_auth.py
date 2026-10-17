def test_signup_and_login(client):
    payload = {"email": "user@example.com", "full_name": "River User", "password": "a-strong-password"}
    signup = client.post("/api/auth/register", json=payload)
    assert signup.status_code == 201
    assert signup.json()["user"]["role"] == "customer"
    assert "password" not in signup.json()["user"]
    assert "password_hash" not in signup.json()["user"]

    login = client.post("/api/auth/login", json={"email": payload["email"].upper(), "password": payload["password"]})
    assert login.status_code == 200
    assert login.json()["user"]["email"] == payload["email"]


def test_signup_rejects_duplicate_email(client):
    payload = {"email": "duplicate@example.com", "full_name": "First User", "password": "a-strong-password"}
    assert client.post("/api/auth/register", json=payload).status_code == 201
    duplicate = {**payload, "email": payload["email"].upper()}
    assert client.post("/api/auth/register", json=duplicate).status_code == 409


def test_login_rejects_wrong_password(client):
    client.post(
        "/api/auth/register",
        json={"email": "wrong@example.com", "full_name": "Wrong User", "password": "a-strong-password"},
    )
    response = client.post("/api/auth/login", json={"email": "wrong@example.com", "password": "not-the-password"})
    assert response.status_code == 401


def test_authenticated_profile_requires_valid_token(client, registered_user):
    token, profile = registered_user
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["id"] == profile["id"]
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer invalid"}).status_code == 401


def test_home_and_existing_boat_endpoint_are_unchanged(client):
    assert client.get("/").json()["status"] == "running"
    boats = client.get("/api/boats").json()["boats"]
    assert [boat["name"] for boat in boats] == ["Ocean Explorer", "Blue Pearl"]


def test_registration_validates_email_and_password(client):
    invalid_email = client.post(
        "/api/auth/register",
        json={"email": "not-an-email", "full_name": "Test User", "password": "a-strong-password"},
    )
    short_password = client.post(
        "/api/auth/register",
        json={"email": "valid@example.com", "full_name": "Test User", "password": "short"},
    )
    assert invalid_email.status_code == 422
    assert short_password.status_code == 422
