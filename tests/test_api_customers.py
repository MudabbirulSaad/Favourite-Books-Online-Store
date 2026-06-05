from conftest import customer_payload


def test_customer_registration_logs_customer_into_session(api_client, valid_customer_payload):
    response = api_client.post("/api/customers", json=valid_customer_payload)

    assert response.status_code == 201
    assert response.get_json()["email"] == "saad@example.com"
    assert api_client.get("/api/session/customer").get_json()["email"] == "saad@example.com"


def test_customer_logout_clears_session(api_client, valid_customer_payload):
    api_client.post("/api/customers", json=valid_customer_payload)

    response = api_client.post("/api/logout")

    assert response.status_code == 200
    assert api_client.get("/api/session/customer").get_json() is None


def test_customer_login_restores_session_with_valid_password(api_client, valid_customer_payload):
    api_client.post("/api/customers", json=valid_customer_payload)
    api_client.post("/api/logout")

    response = api_client.post("/api/login", json={"email": "saad@example.com", "password": "secret123"})

    assert response.status_code == 200
    assert api_client.get("/api/session/customer").get_json()["email"] == "saad@example.com"


def test_customer_login_rejects_invalid_password(api_client, valid_customer_payload):
    api_client.post("/api/customers", json=valid_customer_payload)

    response = api_client.post("/api/login", json={"email": "saad@example.com", "password": "wrong-password"})

    assert response.status_code == 400


def test_customer_registration_rejects_malformed_email(api_client):
    response = api_client.post("/api/customers", json=customer_payload("not-an-email"))

    assert response.status_code == 400
    assert response.get_json()["message"] == "Customer email must be a valid email address."


def test_customer_registration_normalises_email_to_lowercase(api_client):
    response = api_client.post("/api/customers", json=customer_payload("SAAD@EXAMPLE.COM"))

    assert response.status_code == 201
    assert response.get_json()["email"] == "saad@example.com"
