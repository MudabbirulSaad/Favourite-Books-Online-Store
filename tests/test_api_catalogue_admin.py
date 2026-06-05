from conftest import register_customer


def valid_admin_catalogue_payload(item):
    return {
        "employee_id": "emp-1",
        "access_code": "staff-code",
        "item": item,
    }


def test_books_endpoint_combines_search_and_sort(api_client):
    response = api_client.get("/api/books?q=ray&sort=pages")

    assert response.status_code == 200
    assert [book["name"] for book in response.get_json()] == ["Fahrenheit 451"]


def test_employee_can_add_catalogue_item(api_client):
    response = api_client.post("/api/catalogue/items", json=valid_admin_catalogue_payload({
        "item_type": "ebook",
        "isbn": 77,
        "name": "Architecture Field Guide",
        "author": "A. Designer",
        "genre": "Technology",
        "edition": "EPUB",
        "pages": 144,
        "price": "12.50",
    }))

    assert response.status_code == 201
    assert response.get_json()["item"]["item_type"] == "ebook"
    books = api_client.get("/api/books?q=Architecture").get_json()
    assert "Architecture Field Guide" in [book["name"] for book in books]


def test_employee_can_update_and_delete_catalogue_item(api_client):
    api_client.post("/api/catalogue/items", json=valid_admin_catalogue_payload({
        "item_type": "book",
        "isbn": 88,
        "name": "Draft Title",
        "author": "A. Designer",
        "genre": "Technology",
        "edition": "First",
        "pages": 120,
        "price": "18.50",
        "stock": 5,
    }))

    detail = api_client.get("/api/catalogue/items/88")
    update_response = api_client.patch("/api/catalogue/items/88", json=valid_admin_catalogue_payload({
        "name": "Final Title",
        "price": "20.00",
        "stock": 4,
    }))
    delete_response = api_client.delete("/api/catalogue/items/88", json={
        "employee_id": "emp-1",
        "access_code": "staff-code",
    })

    assert detail.status_code == 200
    assert detail.get_json()["name"] == "Draft Title"
    assert update_response.status_code == 200
    assert update_response.get_json()["item"]["name"] == "Final Title"
    assert api_client.get("/api/catalogue/items/88").status_code == 404
    assert delete_response.status_code == 200


def test_catalogue_admin_api_rejects_invalid_item_data(api_client):
    base_item = {
        "item_type": "book",
        "isbn": 88,
        "name": "Draft Title",
        "author": "A. Designer",
        "genre": "Technology",
        "edition": "First",
        "pages": 120,
        "price": "18.50",
        "stock": 5,
    }
    cases = [
        ({"stock": -1}, "Stock must be at least 0."),
        ({"price": "0"}, "Price must be at least 0.01."),
        ({"pages": 0}, "Pages must be at least 1."),
        ({"author": ""}, "Author is required."),
        ({"genre": ""}, "Genre is required."),
        ({"name": ""}, "Catalogue item name is required."),
        ({"item_type": "audio"}, "Catalogue item type must be book, ebook, or merchandise."),
    ]

    for override, message in cases:
        response = api_client.post(
            "/api/catalogue/items",
            json=valid_admin_catalogue_payload({**base_item, **override}),
        )
        assert response.status_code == 400
        assert response.get_json()["message"] == message


def test_catalogue_admin_api_rejects_merchandise_without_category(api_client):
    response = api_client.post("/api/catalogue/items", json=valid_admin_catalogue_payload({
        "item_type": "merchandise",
        "sku": 89,
        "name": "Blank Category Tote",
        "category": "",
        "price": "12.00",
        "stock": 4,
    }))

    assert response.status_code == 400
    assert response.get_json()["message"] == "Category is required."


def test_employee_cannot_delete_catalogue_item_used_by_order(api_client, valid_checkout_payload):
    api_client.post("/api/cart/items", json={"book_id": 1})
    register_customer(api_client)
    api_client.post("/api/checkout", json=valid_checkout_payload)

    response = api_client.delete("/api/catalogue/items/1", json={
        "employee_id": "emp-1",
        "access_code": "staff-code",
    })

    assert response.status_code == 400
    assert "cannot be deleted" in response.get_json()["message"]
