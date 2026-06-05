from decimal import Decimal

import pytest

from favourite_books.domain.cart import InvalidQuantityError, ItemOrder, ShoppingCart
from favourite_books.domain.items import Book


def book(isbn=1, price="21.99"):
    return Book(isbn, "The Great Gatsby", "F. Scott Fitzgerald", "Classic", "First", 180, 0, price)


def test_cart_combines_matching_books_and_uses_decimal_totals():
    cart = ShoppingCart()

    cart.add_item(book(), quantity=1)
    cart.add_item(book(), quantity=2)

    assert cart.total_items() == 3
    assert cart.subtotal() == Decimal("65.97")
    assert cart.to_list()[0]["line_total"] == "65.97"


def test_cart_remove_and_clear():
    cart = ShoppingCart()
    cart.add_item(book(1))
    cart.add_item(book(2))

    assert cart.remove_item(1) is True
    assert cart.remove_item(99) is False
    cart.clear()

    assert cart.orders == []


def test_item_order_rejects_invalid_quantities():
    with pytest.raises(InvalidQuantityError, match="at least 1"):
        ItemOrder(book(), 0)

    with pytest.raises(InvalidQuantityError, match="cannot exceed 20"):
        ItemOrder(book(), 21)


def test_cart_quantity_limit_is_a_domain_invariant():
    cart = ShoppingCart()

    cart.add_item(book(), quantity=20)

    with pytest.raises(InvalidQuantityError, match="cannot exceed 20"):
        cart.add_item(book())

    assert cart.to_list()[0]["quantity"] == 20
