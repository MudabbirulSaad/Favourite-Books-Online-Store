from decimal import Decimal

from favourite_books.domain.cart import ItemOrder
from favourite_books.domain.checkout import Order
from favourite_books.domain.customer import Address, Customer
from favourite_books.domain.items import Book


def test_order_totals_include_postcode_shipping_and_tax():
    customer = Customer.guest(
        "Saad",
        "saad@example.com",
        Address("1 Main St", "Melbourne", "VIC", "3000"),
    )
    book = Book(1, "The Great Gatsby", "F. Scott Fitzgerald", "Classic", "First", 180, 0, "21.99")

    order = Order(customer, [ItemOrder(book, 2)], "PAY-1", order_id="ORDER-1")

    assert order.subtotal == Decimal("43.98")
    assert order.shipping == Decimal("3.99")
    assert order.tax == Decimal("4.40")
    assert order.total == Decimal("52.37")
    assert order.to_dict()["order_id"] == "ORDER-1"
