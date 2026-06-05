import pytest

from favourite_books.application.services import CatalogueService, NotFoundError, ValidationError
from favourite_books.domain.customer import Employee
from favourite_books.domain.items import Book, EBook


def test_employee_can_add_catalogue_item_with_factory(sqlite_repositories):
    items = sqlite_repositories["books"]
    employees = sqlite_repositories["employees"]
    employees.add(Employee("emp-1", "Store Owner", "staff-code"))
    service = CatalogueService(items, employees=employees)

    result = service.add_catalogue_item(
        "emp-1",
        "staff-code",
        {
            "item_type": "ebook",
            "isbn": 77,
            "name": "Architecture Field Guide",
            "author": "A. Designer",
            "genre": "Technology",
            "edition": "EPUB",
            "pages": 144,
            "price": "12.50",
        },
    )

    assert result["item"]["name"] == "Architecture Field Guide"
    assert isinstance(items.by_isbn(77), EBook)


def test_employee_cannot_add_duplicate_catalogue_item(sqlite_repositories):
    items = sqlite_repositories["books"]
    employees = sqlite_repositories["employees"]
    items.add(Book(1, "The Great Gatsby", "F. Scott Fitzgerald", "Classic", "First", 180, 0, "21.99"))
    employees.add(Employee("emp-1", "Store Owner", "staff-code"))
    service = CatalogueService(items, employees=employees)

    with pytest.raises(ValidationError, match="already exists"):
        service.add_catalogue_item(
            "emp-1",
            "staff-code",
            {
                "item_type": "book",
                "isbn": 1,
                "name": "Duplicate",
                "author": "Someone",
                "genre": "Classic",
                "edition": "First",
                "pages": 100,
                "price": "10.00",
            },
        )


def test_catalogue_admin_service_rejects_unknown_employee(sqlite_repositories):
    service = CatalogueService(sqlite_repositories["books"], employees=sqlite_repositories["employees"])

    with pytest.raises(NotFoundError, match="Employee not found"):
        service.add_catalogue_item("missing", "staff-code", {})
