import re
from decimal import Decimal, InvalidOperation
from typing import Protocol

from favourite_books.domain.cart import InvalidQuantityError, ItemOrder, ShoppingCart
from favourite_books.domain.analytics import WebsiteAnalytics
from favourite_books.domain.checkout import (
    CreditCard,
    Order,
    PaymentResult,
    credit_card_from_dict,
)
from favourite_books.domain.customer import Customer, Employee
from favourite_books.domain.checkout import address_from_dict
from favourite_books.domain.items import Item, ItemFactory, OutOfStockError

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


class ItemRepository(Protocol):
    def add(self, item: Item) -> None:
        pass

    def all(self) -> list[Item]:
        pass

    def by_isbn(self, isbn: int) -> Item | None:
        pass

    def save(self, item: Item) -> None:
        pass

    def delete(self, item_id: int) -> None:
        pass

    def is_referenced(self, item_id: int) -> bool:
        pass


BookRepository = ItemRepository


class CartRepository(Protocol):
    def get(self, cart_id: str) -> ShoppingCart:
        pass

    def save(self, cart_id: str, cart: ShoppingCart) -> None:
        pass


class OrderRepository(Protocol):
    def add(self, order: Order) -> None:
        pass

    def all(self) -> list[Order]:
        pass


class PaymentGateway(Protocol):
    def authorise(self, card: CreditCard, amount: Decimal) -> PaymentResult:
        pass


class AnalyticsRepository(Protocol):
    def get(self) -> WebsiteAnalytics:
        pass

    def save(self, analytics: WebsiteAnalytics) -> None:
        pass


class CustomerRepository(Protocol):
    def add(self, customer: Customer, password: str) -> None:
        pass

    def by_email(self, email: str) -> Customer | None:
        pass

    def authenticate(self, email: str, password: str) -> Customer | None:
        pass


class EmployeeRepository(Protocol):
    def add(self, employee: Employee) -> None:
        pass

    def by_id(self, employee_id: str) -> Employee | None:
        pass


class ValidationError(Exception):
    """Raised when user input does not satisfy application rules."""


class NotFoundError(Exception):
    """Raised when a requested domain object does not exist."""


class CatalogueService:
    SORT_FIELDS = {"author", "pages", "genre", "original"}

    def __init__(
        self,
        books: ItemRepository,
        analytics: AnalyticsRepository | None = None,
        employees: EmployeeRepository | None = None,
    ):
        self.books = books
        self.analytics = analytics
        self.employees = employees

    def list_books(self, sort: str = "original", query: str = "") -> list[Item]:
        if sort not in self.SORT_FIELDS:
            raise ValidationError("Invalid sort option.")

        if self.analytics:
            analytics = self.analytics.get()
            analytics.record_site_visit()
            self.analytics.save(analytics)

        books = self.books.all()
        q = query.lower().strip()
        if q:
            books = [
                book
                for book in books
                if q in book.name.lower()
                or q in getattr(book, "author", "").lower()
                or q in getattr(book, "category", "").lower()
            ]

        key_map = {
            "author": lambda book: getattr(book, "author", "").lower(),
            "pages": lambda book: getattr(book, "pages", 0),
            "genre": lambda book: getattr(book, "genre", getattr(book, "category", "")).lower(),
            "original": lambda book: book.item_id,
        }
        return sorted(books, key=key_map[sort])

    def record_item_view(self, item_id: int) -> dict:
        item = self.books.by_isbn(item_id)
        if not item:
            raise NotFoundError("Catalogue item not found.")
        if not self.analytics:
            raise ValidationError("Analytics are not configured.")

        analytics = self.analytics.get()
        analytics.record_item_view(item_id)
        self.analytics.save(analytics)
        return {"message": f"Recorded view for {item.name}."}

    def add_catalogue_item(
        self,
        employee_id: str,
        access_code: str,
        item_data: dict,
    ) -> dict:
        self._require_employee(employee_id, access_code)
        item_data = self._validated_item_data(item_data)

        try:
            item = ItemFactory.create(item_data)
        except (KeyError, ValueError) as exc:
            raise ValidationError(f"Catalogue item data is invalid: {exc}") from exc

        if self.books.by_isbn(item.item_id):
            raise ValidationError("Catalogue item already exists.")

        self.books.add(item)
        return {
            "message": f"Catalogue item {item.item_id} added.",
            "item": item.to_dict(),
        }

    def get_catalogue_item(self, item_id: int) -> dict:
        item = self.books.by_isbn(item_id)
        if not item:
            raise NotFoundError("Catalogue item not found.")
        return item.to_dict()

    def update_catalogue_item(
        self,
        item_id: int,
        employee_id: str,
        access_code: str,
        item_data: dict,
    ) -> dict:
        self._require_employee(employee_id, access_code)
        existing = self.books.by_isbn(item_id)
        if not existing:
            raise NotFoundError("Catalogue item not found.")

        merged = {
            **existing.to_dict(),
            **{key: value for key, value in item_data.items() if value is not None},
        }
        merged["item_type"] = existing.item_type
        if existing.item_type == "merchandise":
            merged["sku"] = item_id
            merged["category"] = merged.get("category") or merged.get("genre")
        else:
            merged["isbn"] = item_id

        merged = self._validated_item_data(merged)
        try:
            item = ItemFactory.create(merged)
        except (KeyError, ValueError) as exc:
            raise ValidationError(f"Catalogue item data is invalid: {exc}") from exc

        self.books.save(item)
        return {
            "message": f"Catalogue item {item.item_id} updated.",
            "item": item.to_dict(),
        }

    def delete_catalogue_item(self, item_id: int, employee_id: str, access_code: str) -> dict:
        self._require_employee(employee_id, access_code)
        item = self.books.by_isbn(item_id)
        if not item:
            raise NotFoundError("Catalogue item not found.")
        if self.books.is_referenced(item_id):
            raise ValidationError("Catalogue item cannot be deleted because it is used by a cart or order.")

        self.books.delete(item_id)
        return {"message": f"Catalogue item {item_id} deleted."}

    def _require_employee(self, employee_id: str, access_code: str) -> Employee:
        if not self.employees:
            raise ValidationError("Employee catalogue management is not configured.")
        employee = self.employees.by_id(employee_id)
        if not employee:
            raise NotFoundError("Employee not found.")
        if not employee.can_manage_catalogue(access_code):
            raise ValidationError("Employee access code is invalid.")
        return employee

    def _validated_item_data(self, raw: dict) -> dict:
        data = dict(raw or {})
        item_type = str(data.get("item_type", "book") or "book").strip().lower()
        if item_type not in {"book", "ebook", "merchandise"}:
            raise ValidationError("Catalogue item type must be book, ebook, or merchandise.")

        identifier_key = "sku" if item_type == "merchandise" else "isbn"
        data["item_type"] = item_type
        data[identifier_key] = require_int(data.get(identifier_key), "ISBN / SKU", minimum=1)
        data["name"] = require_text(data.get("name"), "Catalogue item name")
        data["price"] = f"{require_decimal(data.get('price'), 'Price', minimum=Decimal('0.01')):.2f}"
        data["stock"] = require_int(data.get("stock", 10 if item_type != "ebook" else 9999), "Stock", minimum=0)

        if item_type in {"book", "ebook"}:
            data["author"] = require_text(data.get("author"), "Author")
            data["genre"] = require_text(data.get("genre"), "Genre")
            data["edition"] = require_text(data.get("edition"), "Edition")
            data["pages"] = require_int(data.get("pages"), "Pages", minimum=1)
            if item_type == "ebook":
                data["file_format"] = require_text(data.get("file_format", "EPUB"), "File format")
            return data

        data["category"] = require_text(data.get("category") or data.get("genre"), "Category")
        return data


class CustomerService:
    def __init__(self, customers: CustomerRepository):
        self.customers = customers

    def register_customer(self, data: dict) -> dict:
        email = str(data.get("email", "")).strip().lower()
        password = str(data.get("password", "")).strip()
        if not email:
            raise ValidationError("Customer email is required.")
        if not EMAIL_PATTERN.match(email):
            raise ValidationError("Customer email must be a valid email address.")
        if len(password) < 6:
            raise ValidationError("Password must contain at least 6 characters.")
        if self.customers.by_email(email):
            raise ValidationError("Customer email is already registered.")

        try:
            customer = Customer(
                email,
                data.get("name", ""),
                email,
                address_from_dict(data.get("shipping_address", {})),
            )
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

        self.customers.add(customer, password)
        return customer.to_dict()

    def login(self, email: str, password: str) -> dict:
        customer = self.customers.authenticate(email, password)
        if not customer:
            raise ValidationError("Invalid email address or password.")
        return customer.to_dict()

    def by_email(self, email: str) -> Customer | None:
        return self.customers.by_email(email)


class CartService:
    MAX_QUANTITY = ItemOrder.MAX_QUANTITY
    SHIPPING = Decimal("3.99")

    def __init__(
        self,
        books: ItemRepository,
        carts: CartRepository,
        orders: OrderRepository | None = None,
        payments: PaymentGateway | None = None,
        analytics: AnalyticsRepository | None = None,
    ):
        self.books = books
        self.carts = carts
        self.orders = orders
        self.payments = payments
        self.analytics = analytics

    def add_book(self, cart_id: str, book_id: int) -> str:
        book = self.books.by_isbn(book_id)
        if not book:
            raise NotFoundError("Book not found")

        cart = self.carts.get(cart_id)
        try:
            cart.add_item(book)
        except InvalidQuantityError as exc:
            raise ValidationError(str(exc)) from exc
        self.carts.save(cart_id, cart)
        return f"'{book.name}' added to cart."

    def get_cart_read_model(self, cart_id: str) -> dict:
        cart = self.carts.get(cart_id)
        return {
            "items": cart.to_list(),
            "summary": self._summary(cart),
        }

    def update_quantity(self, cart_id: str, isbn: int, quantity: int) -> str:
        cart = self.carts.get(cart_id)
        try:
            if not cart.update_quantity(isbn, quantity):
                raise NotFoundError("Cart item not found.")
        except InvalidQuantityError as exc:
            raise ValidationError(str(exc)) from exc
        self.carts.save(cart_id, cart)
        return "Updated"

    def remove_item(self, cart_id: str, isbn: int) -> str:
        cart = self.carts.get(cart_id)
        if not cart.remove_item(isbn):
            raise NotFoundError("Cart item not found.")
        self.carts.save(cart_id, cart)
        return "Removed"

    def checkout(
        self,
        cart_id: str,
        customer: Customer,
        payment_data: dict | None = None,
    ) -> dict:
        cart = self.carts.get(cart_id)
        if not cart.orders:
            raise ValidationError("Cart is empty. Add a book before checkout.")

        if not self.orders or not self.payments or not self.analytics:
            raise ValidationError("Checkout is not configured.")

        try:
            card = credit_card_from_dict(payment_data or {})
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

        for line in cart.orders:
            if not line.item.has_stock(line.quantity):
                raise ValidationError(f"Not enough stock for {line.item.name}.")

        preview_order = Order(customer, cart.orders, "pending")
        payment = self.payments.authorise(card, preview_order.total)
        if not payment.authorised:
            raise ValidationError(payment.message)

        order = Order(customer, cart.orders, payment.reference)
        transaction = getattr(self.books, "transaction", null_transaction)
        try:
            with transaction():
                for line in cart.orders:
                    line.item.decrement_stock(line.quantity)
                    self.books.save(line.item)

                self.orders.add(order)
                analytics = self.analytics.get()
                analytics.record_order(order)
                self.analytics.save(analytics)

                cart.clear()
                self.carts.save(cart_id, cart)
        except OutOfStockError as exc:
            raise ValidationError(str(exc)) from exc

        return {
            "message": (
                f"Order {order.order_id} confirmed for {order.total_items} item"
                f"{'' if order.total_items == 1 else 's'}. Total: ${order.total:.2f}."
            ),
            "order": order.to_dict(),
        }

    def _summary(self, cart: ShoppingCart) -> dict:
        subtotal = cart.subtotal()
        requires_shipping = any(line.requires_shipping for line in cart.orders)
        shipping = self.SHIPPING if requires_shipping else Decimal("0.00")
        total = subtotal + shipping
        return {
            "total_items": cart.total_items(),
            "subtotal": f"{subtotal:.2f}",
            "shipping": f"{shipping:.2f}",
            "total": f"{total:.2f}",
            "requires_shipping": requires_shipping,
        }


class null_transaction:
    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc, traceback):
        return False


def require_text(value, field_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValidationError(f"{field_name} is required.")
    return text


def require_int(value, field_name: str, minimum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{field_name} must be a whole number.") from exc
    if parsed < minimum:
        raise ValidationError(f"{field_name} must be at least {minimum}.")
    return parsed


def require_decimal(value, field_name: str, minimum: Decimal) -> Decimal:
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValidationError(f"{field_name} must be a valid amount.") from exc
    if parsed < minimum:
        raise ValidationError(f"{field_name} must be at least {minimum}.")
    return parsed
