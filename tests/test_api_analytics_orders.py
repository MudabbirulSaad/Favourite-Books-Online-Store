from conftest import register_customer


def test_item_view_analytics_endpoint_persists_views(api_client):
    response = api_client.post("/api/analytics/item-views/1")

    analytics = api_client.get("/api/analytics").get_json()

    assert response.status_code == 200
    assert response.get_json()["message"] == "Recorded view for The Great Gatsby."
    assert analytics["most_viewed_items"] == [1]


def test_order_history_and_analytics_reflect_successful_checkout(api_client, valid_checkout_payload):
    api_client.post("/api/cart/items", json={"book_id": 1})
    register_customer(api_client)
    api_client.post("/api/checkout", json=valid_checkout_payload)

    orders = api_client.get("/api/orders").get_json()
    analytics = api_client.get("/api/analytics").get_json()

    assert len(orders) == 1
    assert orders[0]["total"] == "28.18"
    assert analytics["conversion_count"] == 1
