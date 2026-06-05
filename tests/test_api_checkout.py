from conftest import register_customer


def test_checkout_authorises_payment_creates_order_and_clears_cart(api_client, valid_checkout_payload):
    api_client.post("/api/cart/items", json={"book_id": 1})
    api_client.patch("/api/cart/items/1", json={"quantity": 2})
    register_customer(api_client)

    response = api_client.post("/api/checkout", json=valid_checkout_payload)

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["message"].startswith("Order ")
    assert payload["order"]["total_items"] == 2
    assert payload["order"]["subtotal"] == "43.98"
    assert payload["order"]["shipping"] == "3.99"
    assert payload["order"]["tax"] == "4.40"
    assert payload["order"]["total"] == "52.37"
    assert payload["order"]["customer"]["customer_id"] == "saad@example.com"
    assert payload["order"]["customer"]["email"] == "saad@example.com"
    assert payload["order"]["payment_status"] == "authorised"
    assert api_client.get("/api/cart").get_json()["items"] == []


def test_declined_payment_preserves_cart(api_client, declined_card_payload):
    api_client.post("/api/cart/items", json={"book_id": 1})
    register_customer(api_client)

    response = api_client.post("/api/checkout", json=declined_card_payload)

    assert response.status_code == 400
    assert "declined" in response.get_json()["message"]
    assert api_client.get("/api/cart").get_json()["items"][0]["quantity"] == 1


def test_checkout_requires_logged_in_customer(api_client):
    api_client.post("/api/cart/items", json={"book_id": 1})

    response = api_client.post("/api/checkout", json={})

    assert response.status_code == 401
    assert response.get_json()["message"] == "Login is required before checkout."


def test_checkout_requires_payment_data_after_login(api_client):
    api_client.post("/api/cart/items", json={"book_id": 1})
    register_customer(api_client)

    response = api_client.post("/api/checkout", json={})

    assert response.status_code == 400
    assert response.get_json()["message"] == "Cardholder is required."


def test_ebook_only_checkout_has_no_shipping(api_client, valid_checkout_payload):
    api_client.post("/api/cart/items", json={"book_id": 7})
    register_customer(api_client, postcode="2000")

    response = api_client.post("/api/checkout", json=valid_checkout_payload)

    assert response.status_code == 200
    assert response.get_json()["order"]["shipping"] == "0.00"
    assert response.get_json()["order"]["total"] == "10.99"
