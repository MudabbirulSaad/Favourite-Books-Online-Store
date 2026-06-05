import pytest

from favourite_books.domain.items import Book, EBook, ItemFactory, Merchandise, OutOfStockError


def test_item_factory_creates_book_ebook_and_merchandise_subclasses():
    book = ItemFactory.create({
        "item_type": "book",
        "isbn": 1,
        "name": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "genre": "Classic",
        "edition": "First",
        "pages": 180,
        "price": "21.99",
        "stock": 4,
    })
    ebook = ItemFactory.create({
        "item_type": "ebook",
        "isbn": 7,
        "name": "Digital Design",
        "author": "A. Writer",
        "genre": "Technology",
        "edition": "PDF",
        "pages": 210,
        "price": "9.99",
    })
    merchandise = ItemFactory.create({
        "item_type": "merchandise",
        "sku": 1001,
        "name": "Favourite Books Tote",
        "category": "Accessories",
        "price": "14.50",
    })

    assert isinstance(book, Book)
    assert isinstance(ebook, EBook)
    assert isinstance(merchandise, Merchandise)
    assert book.stock == 4
    assert ebook.item_type == "ebook"
    assert merchandise.item_id == 1001


def test_stock_decrement_rejects_overselling():
    book = Book(1, "The Great Gatsby", "F. Scott Fitzgerald", "Classic", "First", 180, 0, "21.99", stock=1)

    with pytest.raises(OutOfStockError):
        book.decrement_stock(2)

    book.decrement_stock(1)

    assert book.stock == 0
