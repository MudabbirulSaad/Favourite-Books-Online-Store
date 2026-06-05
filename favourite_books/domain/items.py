from abc import ABC, abstractmethod
from decimal import Decimal


class Item(ABC):
    """Base item interface from the Assignment 2 catalogue model."""

    def __init__(self, stock_num: int, name: str, price: Decimal | str | float):
        self.stock_num = stock_num
        self.name = name
        self.price = Decimal(str(price))
        self.stock = 0

    @abstractmethod
    def get_price(self) -> Decimal:
        pass

    @property
    @abstractmethod
    def item_type(self) -> str:
        pass

    @property
    def item_id(self) -> int:
        return self.stock_num

    def has_stock(self, quantity: int) -> bool:
        return self.stock >= quantity

    def decrement_stock(self, quantity: int) -> None:
        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")
        if not self.has_stock(quantity):
            raise OutOfStockError(f"Not enough stock for {self.name}.")
        self.stock -= quantity

    def to_dict(self) -> dict:
        return {
            "isbn": self.item_id,
            "stock_num": self.stock_num,
            "name": self.name,
            "price": f"{self.price:.2f}",
            "item_type": self.item_type,
            "stock": self.stock,
        }


class OutOfStockError(Exception):
    """Raised when an item cannot supply the requested quantity."""


class TangibleItem(Item):
    """Assignment 2 tangible item base used by physical catalogue items."""

    def __init__(
        self,
        stock_num: int,
        name: str,
        price: Decimal | str | float,
        weight_grams: int = 0,
        stock: int = 10,
    ):
        super().__init__(stock_num, name, price)
        self.weight_grams = weight_grams
        self.stock = stock


class Book(TangibleItem):
    """Physical book from the Assignment 2 object model."""

    def __init__(
        self,
        isbn: int,
        name: str,
        author: str,
        genre: str,
        edition: str,
        pages: int,
        cover: int,
        price: Decimal | str | float,
        stock: int = 10,
    ):
        super().__init__(isbn, name, price, stock=stock)
        self.isbn = isbn
        self.author = author
        self.genre = genre
        self.edition = edition
        self.pages = pages
        self.cover = cover

    def get_price(self) -> Decimal:
        return self.price

    @property
    def item_type(self) -> str:
        return "book"

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "isbn": self.isbn,
            "author": self.author,
            "genre": self.genre,
            "edition": self.edition,
            "pages": self.pages,
            "cover": self.cover,
        }


class EBook(Item):
    """Digital book variant from the Assignment 2 product hierarchy."""

    def __init__(
        self,
        isbn: int,
        name: str,
        author: str,
        genre: str,
        edition: str,
        pages: int,
        file_format: str,
        price: Decimal | str | float,
        stock: int = 9999,
    ):
        super().__init__(isbn, name, price)
        self.isbn = isbn
        self.author = author
        self.genre = genre
        self.edition = edition
        self.pages = pages
        self.file_format = file_format
        self.stock = stock

    def get_price(self) -> Decimal:
        return self.price

    @property
    def item_type(self) -> str:
        return "ebook"

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "isbn": self.isbn,
            "author": self.author,
            "genre": self.genre,
            "edition": self.edition,
            "pages": self.pages,
            "cover": 0,
            "file_format": self.file_format,
        }


class Merchandise(TangibleItem):
    """Non-book merchandise item from the Assignment 2 product hierarchy."""

    def __init__(
        self,
        sku: int,
        name: str,
        category: str,
        price: Decimal | str | float,
        stock: int = 10,
    ):
        super().__init__(sku, name, price, stock=stock)
        self.sku = sku
        self.category = category

    def get_price(self) -> Decimal:
        return self.price

    @property
    def item_type(self) -> str:
        return "merchandise"

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "isbn": self.sku,
            "author": "Favourite Books",
            "genre": self.category,
            "edition": "Merchandise",
            "pages": 0,
            "cover": 0,
            "category": self.category,
        }


class ItemFactory:
    """Factory Method-style creator for Assignment 2 catalogue item variants."""

    @staticmethod
    def create(raw: dict) -> Item:
        item_type = raw.get("item_type", "book")
        if item_type == "book":
            return Book(
                raw["isbn"],
                raw["name"],
                raw["author"],
                raw["genre"],
                raw["edition"],
                raw["pages"],
                raw.get("cover", 0),
                raw["price"],
                raw.get("stock", 10),
            )
        if item_type == "ebook":
            return EBook(
                raw["isbn"],
                raw["name"],
                raw["author"],
                raw["genre"],
                raw["edition"],
                raw["pages"],
                raw.get("file_format", "EPUB"),
                raw["price"],
                raw.get("stock", 9999),
            )
        if item_type == "merchandise":
            return Merchandise(
                raw["sku"],
                raw["name"],
                raw["category"],
                raw["price"],
                raw.get("stock", 10),
            )
        raise ValueError(f"Unsupported item type: {item_type}")
