import pytest

from favourite_books.application.services import CartService, ValidationError
from favourite_books.domain.items import EBook


def test_cart_repository_isolates_read_models_by_session_id(seeded_catalogue):
    service = CartService(seeded_catalogue["books"], seeded_catalogue["carts"])

    service.add_book("cart-a", 1)
    service.add_book("cart-b", 2)

    assert service.get_cart_read_model("cart-a")["items"][0]["name"] == "The Great Gatsby"
    assert service.get_cart_read_model("cart-b")["items"][0]["name"] == "Fahrenheit 451"


def test_cart_quantity_limit_is_enforced_before_mutation(seeded_catalogue):
    service = CartService(seeded_catalogue["books"], seeded_catalogue["carts"])

    for _ in range(service.MAX_QUANTITY):
        service.add_book("cart-a", 1)

    with pytest.raises(ValidationError):
        service.add_book("cart-a", 1)

    assert service.get_cart_read_model("cart-a")["items"][0]["quantity"] == service.MAX_QUANTITY


def test_cart_read_model_contains_authoritative_summary(seeded_catalogue):
    service = CartService(seeded_catalogue["books"], seeded_catalogue["carts"])

    service.add_book("cart-a", 1)
    service.add_book("cart-a", 1)
    cart = service.get_cart_read_model("cart-a")

    assert cart["items"][0]["quantity"] == 2
    assert cart["summary"] == {
        "total_items": 2,
        "subtotal": "43.98",
        "shipping": "3.99",
        "total": "47.97",
        "requires_shipping": True,
    }


def test_empty_cart_read_model_has_zero_summary(seeded_catalogue):
    service = CartService(seeded_catalogue["books"], seeded_catalogue["carts"])

    cart = service.get_cart_read_model("cart-a")

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


def test_ebook_only_cart_read_model_does_not_add_shipping(seeded_catalogue):
    seeded_catalogue["books"].add(
        EBook(7, "Clean Architecture Notes", "S. Martin", "Technology", "EPUB", 210, "EPUB", "9.99")
    )
    service = CartService(seeded_catalogue["books"], seeded_catalogue["carts"])

    service.add_book("cart-a", 7)
    cart = service.get_cart_read_model("cart-a")

    assert cart["summary"] == {
        "total_items": 1,
        "subtotal": "9.99",
        "shipping": "0.00",
        "total": "9.99",
        "requires_shipping": False,
    }


def test_mixed_cart_read_model_requires_shipping(seeded_catalogue):
    seeded_catalogue["books"].add(
        EBook(7, "Clean Architecture Notes", "S. Martin", "Technology", "EPUB", 210, "EPUB", "9.99")
    )
    service = CartService(seeded_catalogue["books"], seeded_catalogue["carts"])

    service.add_book("cart-a", 1)
    service.add_book("cart-a", 7)
    cart = service.get_cart_read_model("cart-a")

    assert cart["summary"] == {
        "total_items": 2,
        "subtotal": "31.98",
        "shipping": "3.99",
        "total": "35.97",
        "requires_shipping": True,
    }
