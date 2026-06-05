import os
from pathlib import Path

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
from favourite_books.application.services import (
    AnalyticsRepository,
    CatalogueService,
    CartService,
    CustomerService,
    OrderRepository,
)
from favourite_books.domain.customer import Employee
from favourite_books.domain.items import ItemFactory


def build_services(db_path: str | Path | None = None) -> tuple[
    CatalogueService,
    CartService,
    CustomerService,
    OrderRepository,
    AnalyticsRepository,
]:
    database = SQLiteDatabase(db_path or default_database_path())
    database.initialise()

    item_repository = SQLiteBookRepository(database)
    cart_repository = SQLiteCartRepository(database, item_repository)
    order_repository = SQLiteOrderRepository(database, item_repository)
    payment_gateway = FakePaymentGateway()
    analytics_repository = SQLiteAnalyticsRepository(database)
    customer_repository = SQLiteCustomerRepository(database)
    employee_repository = SQLiteEmployeeRepository(database)

    seed_database(item_repository, employee_repository)

    return (
        CatalogueService(item_repository, analytics_repository, employee_repository),
        CartService(
            item_repository,
            cart_repository,
            order_repository,
            payment_gateway,
            analytics_repository,
        ),
        CustomerService(customer_repository),
        order_repository,
        analytics_repository,
    )


def default_database_path() -> Path:
    configured = os.environ.get("BOOKSTORE_DB_PATH")
    if configured:
        return Path(configured)
    return Path(__file__).resolve().parents[1] / "instance" / "favourite_books.sqlite"


def seed_database(item_repository: SQLiteBookRepository, employee_repository: SQLiteEmployeeRepository) -> None:
    employee_repository.add(Employee("emp-1", "Store Owner", "staff-code"))
    if item_repository.all():
        return

    for raw in [
        {"item_type": "book", "isbn": 1, "name": "The Great Gatsby", "author": "F. Scott Fitzgerald", "genre": "Classic", "edition": "First", "pages": 180, "cover": 0, "price": "21.99", "stock": 12},
        {"item_type": "book", "isbn": 2, "name": "To Kill a Mockingbird", "author": "Harper Lee", "genre": "Classic", "edition": "First", "pages": 336, "cover": 1, "price": "25.00", "stock": 8},
        {"item_type": "book", "isbn": 3, "name": "Fahrenheit 451", "author": "Ray Bradbury", "genre": "Sci-Fi", "edition": "Original", "pages": 256, "cover": 2, "price": "19.99", "stock": 10},
        {"item_type": "book", "isbn": 4, "name": "Nineteen Eighty-Four", "author": "George Orwell", "genre": "Dystopian", "edition": "Penguin", "pages": 328, "cover": 3, "price": "23.99", "stock": 9},
        {"item_type": "book", "isbn": 5, "name": "Pride and Prejudice", "author": "Jane Austen", "genre": "Romance", "edition": "Oxford", "pages": 432, "cover": 4, "price": "26.99", "stock": 7},
        {"item_type": "book", "isbn": 6, "name": "The Hobbit", "author": "J.R.R. Tolkien", "genre": "Fantasy", "edition": "Revised", "pages": 310, "cover": 5, "price": "15.00", "stock": 14},
        {"item_type": "ebook", "isbn": 7, "name": "Clean Architecture Notes", "author": "S. Martin", "genre": "Technology", "edition": "EPUB", "pages": 210, "file_format": "EPUB", "price": "9.99"},
        {"item_type": "merchandise", "sku": 1001, "name": "Favourite Books Tote", "category": "Accessories", "price": "14.50", "stock": 6},
    ]:
        item_repository.add(ItemFactory.create(raw))
