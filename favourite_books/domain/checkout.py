from decimal import Decimal
from uuid import uuid4

from favourite_books.domain.cart import ItemOrder
from favourite_books.domain.customer import Address, Customer


class CreditCard:
    """Small payment value object used by the fake payment adapter."""

    def __init__(self, cardholder: str, number: str, expiry: str, cvv: str):
        self.cardholder = require_text(cardholder, "Cardholder")
        self.number = digits_only(number)
        self.expiry = require_text(expiry, "Expiry")
        self.cvv = digits_only(cvv)
        if len(self.number) < 12:
            raise ValueError("Card number must contain at least 12 digits.")
        if len(self.cvv) < 3:
            raise ValueError("CVV must contain at least 3 digits.")

    def masked_number(self) -> str:
        return f"**** **** **** {self.number[-4:]}"


class PaymentResult:
    def __init__(self, authorised: bool, message: str, reference: str = ""):
        self.authorised = authorised
        self.message = message
        self.reference = reference


class Order:
    """Completed checkout order created from a shopping cart."""

    TAX_RATE = Decimal("0.10")

    def __init__(
        self,
        customer: Customer,
        items: list[ItemOrder],
        payment_reference: str,
        order_id: str | None = None,
    ):
        if not items:
            raise ValueError("Order must contain at least one item.")
        self.order_id = order_id or uuid4().hex[:12].upper()
        self.customer = customer
        self.items = [ItemOrder(item.item, item.quantity) for item in items]
        self.payment_reference = payment_reference

    @property
    def subtotal(self) -> Decimal:
        return sum((item.line_total() for item in self.items), Decimal("0.00"))

    @property
    def shipping(self) -> Decimal:
        if not any(item.requires_shipping for item in self.items):
            return Decimal("0.00")
        postcode = self.customer.shipping_address.postcode
        return Decimal("3.99") if postcode.startswith("3") else Decimal("7.99")

    @property
    def tax(self) -> Decimal:
        return (self.subtotal * self.TAX_RATE).quantize(Decimal("0.01"))

    @property
    def total(self) -> Decimal:
        return self.subtotal + self.shipping + self.tax

    @property
    def total_items(self) -> int:
        return sum(item.quantity for item in self.items)

    def to_dict(self) -> dict:
        return {
            "order_id": self.order_id,
            "customer": self.customer.to_dict(),
            "items": [item.to_dict() for item in self.items],
            "payment_reference": self.payment_reference,
            "total_items": self.total_items,
            "subtotal": f"{self.subtotal:.2f}",
            "shipping": f"{self.shipping:.2f}",
            "tax": f"{self.tax:.2f}",
            "total": f"{self.total:.2f}",
            "payment_status": "authorised",
        }


def address_from_dict(data: dict) -> Address:
    return Address(
        data.get("street", ""),
        data.get("city", ""),
        data.get("state", ""),
        data.get("postcode", ""),
    )


def customer_from_dict(data: dict) -> Customer:
    shipping_address = address_from_dict(data.get("shipping_address", {}))
    billing_raw = data.get("billing_address")
    billing_address = address_from_dict(billing_raw) if billing_raw else shipping_address
    return Customer.guest(
        data.get("name", ""),
        data.get("email", ""),
        shipping_address,
        billing_address,
    )


def credit_card_from_dict(data: dict) -> CreditCard:
    return CreditCard(
        data.get("cardholder", ""),
        data.get("number", ""),
        data.get("expiry", ""),
        data.get("cvv", ""),
    )


def digits_only(value: str) -> str:
    return "".join(ch for ch in str(value or "") if ch.isdigit())


def require_text(value: str, field_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field_name} is required.")
    return text
