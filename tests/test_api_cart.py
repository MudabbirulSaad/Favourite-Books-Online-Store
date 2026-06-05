def test_cart_add_update_and_remove_endpoints_return_authoritative_summary(api_client):
    add_response = api_client.post("/api/cart/items", json={"book_id": 1})
    cart_after_add = api_client.get("/api/cart").get_json()

    assert add_response.status_code == 200
    assert "added to cart" in add_response.get_json()["message"]
    assert cart_after_add["items"][0]["quantity"] == 1
    assert cart_after_add["items"][0]["price"] == "21.99"
    assert cart_after_add["summary"] == {
        "total_items": 1,
        "subtotal": "21.99",
        "shipping": "3.99",
        "total": "25.98",
        "requires_shipping": True,
    }

    update_response = api_client.patch("/api/cart/items/1", json={"quantity": 2})
    cart_after_update = api_client.get("/api/cart").get_json()

    assert update_response.status_code == 200
    assert cart_after_update["items"][0]["quantity"] == 2

    delete_response = api_client.delete("/api/cart/items/1")

    assert delete_response.status_code == 200
    assert delete_response.get_json()["message"] == "Removed"
    assert api_client.get("/api/cart").get_json()["items"] == []


def test_empty_cart_summary_has_zero_totals_and_no_shipping(api_client):
    cart = api_client.get("/api/cart").get_json()

    assert cart == {
        "items": [],
        "summary": {
            "total_items": 0,
            "subtotal": "0.00",
            "shipping": "0.00",
            "total": "0.00",
            "requires_shipping": False,
        },
    }


def test_removed_legacy_cart_routes_return_not_found(api_client):
    assert api_client.post("/add_item", json={"book_id": 1}).status_code == 404
    assert api_client.post("/api/cart/update", json={"isbn": 1, "quantity": 2}).status_code == 404
    assert api_client.post("/api/cart/remove", json={"isbn": 1}).status_code == 404


def test_cart_is_scoped_to_browser_session(api_app):
    first_client = api_app.test_client()
    second_client = api_app.test_client()

    first_client.post("/api/cart/items", json={"book_id": 1})

    assert first_client.get("/api/cart").get_json()["items"]
    assert second_client.get("/api/cart").get_json()["items"] == []


def test_invalid_cart_quantity_returns_validation_error(api_client):
    api_client.post("/api/cart/items", json={"book_id": 1})

    response = api_client.patch("/api/cart/items/1", json={"quantity": 0})

    assert response.status_code == 400
    assert response.get_json()["message"] == "Quantity must be at least 1."


def test_ebook_only_cart_has_no_shipping(api_client):
    api_client.post("/api/cart/items", json={"book_id": 7})

    cart = api_client.get("/api/cart").get_json()

    assert cart["summary"] == {
        "total_items": 1,
        "subtotal": "9.99",
        "shipping": "0.00",
        "total": "9.99",
        "requires_shipping": False,
    }


def test_mixed_physical_and_ebook_cart_requires_shipping(api_client):
    api_client.post("/api/cart/items", json={"book_id": 1})
    api_client.post("/api/cart/items", json={"book_id": 7})

    cart = api_client.get("/api/cart").get_json()

    assert cart["summary"] == {
        "total_items": 2,
        "subtotal": "31.98",
        "shipping": "3.99",
        "total": "35.97",
        "requires_shipping": True,
    }
