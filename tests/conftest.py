import sys
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from favourite_books.adapters.payment.fake import FakePaymentGateway
from favourite_books.adapters.sqlite.database import SQLiteDatabase
from favourite_books.adapters.sqlite.repositories import (
    SQLiteAnalyticsRepository,
    SQLiteBookRepository,
    SQLiteCartRepository,
    SQLiteCustomerRepository,
    SQLiteEmployeeRepository,
    SQLiteOrderRepository,
)
from favourite_books.adapters.web.flask_app import create_app
from favourite_books.bootstrap import build_services
from favourite_books.domain.customer import Address, Customer
from favourite_books.domain.items import Book


def make_sqlite_repositories(tmp_path):
    database = SQLiteDatabase(tmp_path / "bookstore.sqlite")
    database.initialise()
    books = SQLiteBookRepository(database)
    return {
        "database": database,
        "books": books,
        "carts": SQLiteCartRepository(database, books),
        "orders": SQLiteOrderRepository(database, books),
        "payments": FakePaymentGateway(),
        "analytics": SQLiteAnalyticsRepository(database),
        "customers": SQLiteCustomerRepository(database),
        "employees": SQLiteEmployeeRepository(database),
    }


def make_app():
    db_path = Path(tempfile.mkdtemp()) / "test.sqlite"
    catalogue_service, cart_service, customer_service, order_repository, analytics_repository = build_services(db_path)
    app = create_app(
        catalogue_service,
        cart_service,
        customer_service,
        order_repository,
        analytics_repository,
    )
    app.config.update(TESTING=True)
    return app


def customer_payload(email="saad@example.com", postcode="3000"):
    return {
        "name": "Saad",
        "email": email,
        "password": "secret123",
        "shipping_address": {
            "street": "1 Main St",
            "city": "Melbourne",
            "state": "VIC",
            "postcode": postcode,
        },
    }


def checkout_payload(card_number="4111111111111111"):
    return {
        "payment": {
            "cardholder": "Saad",
            "number": card_number,
            "expiry": "12/28",
            "cvv": "123",
        },
    }


def checkout_customer():
    return Customer(
        "saad@example.com",
        "Saad",
        "saad@example.com",
        Address("1 Main St", "Melbourne", "VIC", "3000"),
    )


def register_customer(client, email="saad@example.com", postcode="3000"):
    return client.post("/api/customers", json=customer_payload(email, postcode))


def seed_catalogue(repositories):
    repositories["books"].add(
        Book(1, "The Great Gatsby", "F. Scott Fitzgerald", "Classic", "First", 180, 0, "21.99")
    )
    repositories["books"].add(
        Book(2, "Fahrenheit 451", "Ray Bradbury", "Sci-Fi", "Original", 256, 2, "19.99")
    )
    return repositories


@pytest.fixture
def api_app():
    return make_app()


@pytest.fixture
def api_client(api_app):
    return api_app.test_client()


@pytest.fixture
def valid_checkout_payload():
    return checkout_payload()


@pytest.fixture
def declined_card_payload():
    return checkout_payload("4111111111110000")


@pytest.fixture
def valid_customer_payload():
    return customer_payload()


@pytest.fixture
def registered_customer(api_client):
    register_customer(api_client)
    return api_client.get("/api/session/customer").get_json()


@pytest.fixture
def sqlite_repositories(tmp_path):
    return make_sqlite_repositories(tmp_path)


@pytest.fixture
def seeded_catalogue(sqlite_repositories):
    return seed_catalogue(sqlite_repositories)
