import pytest

from favourite_books.adapters.sqlite.database import SQLiteDatabase
from favourite_books.adapters.sqlite.repositories import SQLiteBookRepository
from favourite_books.application.services import CartService, CatalogueService, CustomerService, ValidationError
from favourite_books.domain.customer import Employee
from favourite_books.domain.items import Book, EBook, Merchandise
from conftest import checkout_customer, checkout_payload, customer_payload, make_sqlite_repositories


def test_sqlite_catalogue_repository_reconstructs_item_subclasses(sqlite_repositories, tmp_path):
    sqlite_repositories["books"].add(Book(1, "Book", "Author", "Classic", "First", 100, 0, "10.00", stock=3))
    sqlite_repositories["books"].add(EBook(2, "Digital", "Author", "Tech", "EPUB", 90, "EPUB", "5.00"))
    sqlite_repositories["books"].add(Merchandise(3, "Tote", "Accessories", "15.00", stock=4))

    rebuilt = SQLiteBookRepository(SQLiteDatabase(tmp_path / "bookstore.sqlite"))
    assert [type(item) for item in rebuilt.all()] == [Book, EBook, Merchandise]

    item = rebuilt.by_isbn(1)
    item.name = "Updated Book"
    item.stock = 2
    rebuilt.save(item)

    assert rebuilt.by_isbn(1).name == "Updated Book"
    rebuilt.delete(3)
    assert rebuilt.by_isbn(3) is None


def test_sqlite_cart_customer_order_and_analytics_survive_repository_rebuild(sqlite_repositories, tmp_path):
    sqlite_repositories["books"].add(Book(1, "Book", "Author", "Classic", "First", 100, 0, "10.00", stock=3))

    customer_service = CustomerService(sqlite_repositories["customers"])
    customer_service.register_customer(customer_payload())
    cart_service = CartService(
        sqlite_repositories["books"],
        sqlite_repositories["carts"],
        sqlite_repositories["orders"],
        sqlite_repositories["payments"],
        sqlite_repositories["analytics"],
    )
    cart_service.add_book("cart-a", 1)
    cart_service.checkout("cart-a", checkout_customer(), checkout_payload()["payment"])

    rebuilt = make_sqlite_repositories(tmp_path)
    assert rebuilt["customers"].authenticate("saad@example.com", "secret123").name == "Saad"
    assert rebuilt["books"].by_isbn(1).stock == 2
    assert len(rebuilt["orders"].all()) == 1
    assert rebuilt["analytics"].get().to_dict()["conversion_count"] == 1
    assert rebuilt["carts"].get("cart-a").orders == []


def test_sqlite_customer_repository_hashes_passwords(sqlite_repositories):
    customer_service = CustomerService(sqlite_repositories["customers"])

    customer_service.register_customer(customer_payload())

    with sqlite_repositories["database"].connection() as connection:
        stored = connection.execute("SELECT password FROM customers WHERE email = ?", ("saad@example.com",)).fetchone()

    assert stored["password"] != "secret123"
    assert sqlite_repositories["customers"].authenticate("saad@example.com", "secret123").name == "Saad"
    assert sqlite_repositories["customers"].authenticate("saad@example.com", "wrong-password") is None


def test_sqlite_checkout_rolls_back_when_stock_decrement_fails(sqlite_repositories):
    sqlite_repositories["books"].add(Book(1, "Book", "Author", "Classic", "First", 100, 0, "10.00", stock=1))
    service = CartService(
        sqlite_repositories["books"],
        sqlite_repositories["carts"],
        sqlite_repositories["orders"],
        sqlite_repositories["payments"],
        sqlite_repositories["analytics"],
    )
    service.add_book("cart-a", 1)
    service.update_quantity("cart-a", 1, 2)

    with pytest.raises(ValidationError, match="Not enough stock"):
        service.checkout("cart-a", checkout_customer(), checkout_payload()["payment"])

    assert sqlite_repositories["books"].by_isbn(1).stock == 1
    assert sqlite_repositories["orders"].all() == []
    assert sqlite_repositories["carts"].get("cart-a").orders[0].quantity == 2


def test_sqlite_catalogue_delete_is_blocked_after_order_reference(sqlite_repositories):
    sqlite_repositories["books"].add(Book(1, "Book", "Author", "Classic", "First", 100, 0, "10.00", stock=3))
    sqlite_repositories["employees"].add(Employee("emp-1", "Store Owner", "staff-code"))
    cart_service = CartService(
        sqlite_repositories["books"],
        sqlite_repositories["carts"],
        sqlite_repositories["orders"],
        sqlite_repositories["payments"],
        sqlite_repositories["analytics"],
    )
    catalogue = CatalogueService(sqlite_repositories["books"], employees=sqlite_repositories["employees"])
    cart_service.add_book("cart-a", 1)
    cart_service.checkout("cart-a", checkout_customer(), checkout_payload()["payment"])

    with pytest.raises(ValidationError, match="cannot be deleted"):
        catalogue.delete_catalogue_item(1, "emp-1", "staff-code")
