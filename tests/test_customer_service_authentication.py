import pytest

from conftest import customer_payload
from favourite_books.application.services import CustomerService, ValidationError


def test_customer_service_registers_and_authenticates_customer(sqlite_repositories):
    service = CustomerService(sqlite_repositories["customers"])

    registered = service.register_customer(customer_payload())

    assert registered["email"] == "saad@example.com"
    assert service.login("saad@example.com", "secret123")["name"] == "Saad"


def test_customer_service_rejects_duplicate_email(sqlite_repositories):
    service = CustomerService(sqlite_repositories["customers"])
    payload = customer_payload()

    service.register_customer(payload)

    with pytest.raises(ValidationError, match="already registered"):
        service.register_customer(payload)
