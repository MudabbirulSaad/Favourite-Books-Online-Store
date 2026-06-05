import pytest

from conftest import checkout_customer, checkout_payload
from favourite_books.application.services import CartService, ValidationError
from favourite_books.domain.items import Book
from conftest import make_sqlite_repositories


@pytest.fixture
def repositories(tmp_path):
    repos = make_sqlite_repositories(tmp_path)
    repos["books"].add(Book(1, "The Great Gatsby", "F. Scott Fitzgerald", "Classic", "First", 180, 0, "21.99", stock=2))
    return repos


def make_service(repositories):
    return CartService(
        repositories["books"],
        repositories["carts"],
        repositories["orders"],
        repositories["payments"],
        repositories["analytics"],
    )


def test_checkout_creates_order_updates_inventory_records_analytics_and_clears_cart(repositories):
    service = make_service(repositories)
    service.add_book("cart-a", 1)
    payload = checkout_payload()

    result = service.checkout("cart-a", checkout_customer(), payload["payment"])

    assert result["order"]["total_items"] == 1
    assert result["order"]["subtotal"] == "21.99"
    assert result["order"]["shipping"] == "3.99"
    assert result["order"]["tax"] == "2.20"
    assert result["order"]["total"] == "28.18"
    assert repositories["orders"].all()[0].order_id == result["order"]["order_id"]
    assert repositories["books"].by_isbn(1).stock == 1
    assert repositories["analytics"].get().to_dict()["conversion_count"] == 1
    assert service.get_cart_read_model("cart-a")["items"] == []


def test_failed_payment_preserves_cart_and_stock(repositories):
    service = make_service(repositories)
    service.add_book("cart-a", 1)
    payload = checkout_payload("4111111111110000")

    with pytest.raises(ValidationError, match="declined"):
        service.checkout("cart-a", checkout_customer(), payload["payment"])

    assert service.get_cart_read_model("cart-a")["items"][0]["quantity"] == 1
    assert repositories["books"].by_isbn(1).stock == 2
    assert repositories["orders"].all() == []


def test_checkout_rejects_insufficient_stock_without_clearing_cart(repositories):
    service = make_service(repositories)
    service.add_book("cart-a", 1)
    service.update_quantity("cart-a", 1, 2)
    item = repositories["books"].by_isbn(1)
    item.stock = 1
    repositories["books"].save(item)
    payload = checkout_payload()

    with pytest.raises(ValidationError, match="Not enough stock"):
        service.checkout("cart-a", checkout_customer(), payload["payment"])

    assert service.get_cart_read_model("cart-a")["items"][0]["quantity"] == 2
    assert repositories["orders"].all() == []
