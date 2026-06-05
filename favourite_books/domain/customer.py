class Address:
    """Shipping or billing address from the Assignment 2 customer model."""

    def __init__(self, street: str, city: str, state: str, postcode: str):
        self.street = require_text(street, "Street")
        self.city = require_text(city, "City")
        self.state = require_text(state, "State")
        self.postcode = require_text(postcode, "Postcode")

    def to_dict(self) -> dict:
        return {
            "street": self.street,
            "city": self.city,
            "state": self.state,
            "postcode": self.postcode,
        }


class Customer:
    """Customer/guest checkout data retained in the order record."""

    def __init__(
        self,
        customer_id: str,
        name: str,
        email: str,
        shipping_address: Address,
        billing_address: Address | None = None,
    ):
        self.customer_id = require_text(customer_id, "Customer ID")
        self.name = require_text(name, "Customer name")
        self.email = require_text(email, "Customer email")
        self.shipping_address = shipping_address
        self.billing_address = billing_address or shipping_address

    @classmethod
    def guest(
        cls,
        name: str,
        email: str,
        shipping_address: Address,
        billing_address: Address | None = None,
    ) -> "Customer":
        return cls("guest", name, email, shipping_address, billing_address)

    def to_dict(self) -> dict:
        return {
            "customer_id": self.customer_id,
            "name": self.name,
            "email": self.email,
            "shipping_address": self.shipping_address.to_dict(),
            "billing_address": self.billing_address.to_dict(),
        }


class Employee:
    """Store employee allowed to manage catalogue/inventory records."""

    def __init__(self, employee_id: str, name: str, access_code: str):
        self.employee_id = require_text(employee_id, "Employee ID")
        self.name = require_text(name, "Employee name")
        self.access_code = require_text(access_code, "Employee access code")

    def can_manage_catalogue(self, access_code: str) -> bool:
        return self.access_code == str(access_code or "").strip()


def require_text(value: str, field_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field_name} is required.")
    return text
