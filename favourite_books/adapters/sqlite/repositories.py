from __future__ import annotations

from decimal import Decimal

from werkzeug.security import check_password_hash, generate_password_hash

from favourite_books.adapters.sqlite.database import SQLiteDatabase
from favourite_books.domain.analytics import WebsiteAnalytics
from favourite_books.domain.cart import ShoppingCart
from favourite_books.domain.checkout import Order
from favourite_books.domain.customer import Address, Customer, Employee
from favourite_books.domain.items import Item, ItemFactory


class SQLiteItemRepository:
    def __init__(self, database: SQLiteDatabase):
        self.database = database

    def add(self, item: Item) -> None:
        with self.database.connection() as connection:
            connection.execute(
                """
                INSERT INTO items (
                    item_id, item_type, name, price, stock, author, genre, edition,
                    pages, cover, file_format, category
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                item_values(item),
            )

    def all(self) -> list[Item]:
        with self.database.connection() as connection:
            rows = connection.execute("SELECT * FROM items ORDER BY item_id").fetchall()
        return [item_from_row(row) for row in rows]

    def by_isbn(self, isbn: int) -> Item | None:
        with self.database.connection() as connection:
            row = connection.execute("SELECT * FROM items WHERE item_id = ?", (isbn,)).fetchone()
        return item_from_row(row) if row else None

    def save(self, item: Item) -> None:
        with self.database.connection() as connection:
            connection.execute(
                """
                INSERT INTO items (
                    item_id, item_type, name, price, stock, author, genre, edition,
                    pages, cover, file_format, category
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(item_id) DO UPDATE SET
                    item_type = excluded.item_type,
                    name = excluded.name,
                    price = excluded.price,
                    stock = excluded.stock,
                    author = excluded.author,
                    genre = excluded.genre,
                    edition = excluded.edition,
                    pages = excluded.pages,
                    cover = excluded.cover,
                    file_format = excluded.file_format,
                    category = excluded.category
                """,
                item_values(item),
            )

    def delete(self, item_id: int) -> None:
        with self.database.connection() as connection:
            connection.execute("DELETE FROM items WHERE item_id = ?", (item_id,))

    def is_referenced(self, item_id: int) -> bool:
        with self.database.connection() as connection:
            cart_ref = connection.execute(
                "SELECT 1 FROM cart_items WHERE item_id = ? LIMIT 1",
                (item_id,),
            ).fetchone()
            order_ref = connection.execute(
                "SELECT 1 FROM order_items WHERE item_id = ? LIMIT 1",
                (item_id,),
            ).fetchone()
        return bool(cart_ref or order_ref)

    def transaction(self):
        return self.database.transaction()


SQLiteBookRepository = SQLiteItemRepository


class SQLiteCartRepository:
    def __init__(self, database: SQLiteDatabase, items: SQLiteItemRepository):
        self.database = database
        self.items = items

    def get(self, cart_id: str) -> ShoppingCart:
        with self.database.connection() as connection:
            connection.execute("INSERT OR IGNORE INTO carts (cart_id) VALUES (?)", (cart_id,))
            rows = connection.execute(
                "SELECT item_id, quantity FROM cart_items WHERE cart_id = ? ORDER BY item_id",
                (cart_id,),
            ).fetchall()

        cart = ShoppingCart()
        for row in rows:
            item = self.items.by_isbn(row["item_id"])
            if item:
                cart.add_item(item, row["quantity"])
        return cart

    def save(self, cart_id: str, cart: ShoppingCart) -> None:
        with self.database.connection() as connection:
            connection.execute("INSERT OR IGNORE INTO carts (cart_id) VALUES (?)", (cart_id,))
            connection.execute("DELETE FROM cart_items WHERE cart_id = ?", (cart_id,))
            connection.executemany(
                "INSERT INTO cart_items (cart_id, item_id, quantity) VALUES (?, ?, ?)",
                [(cart_id, line.item.item_id, line.quantity) for line in cart.orders],
            )


class SQLiteOrderRepository:
    def __init__(self, database: SQLiteDatabase, items: SQLiteItemRepository):
        self.database = database
        self.items = items

    def add(self, order: Order) -> None:
        customer = order.customer
        shipping = customer.shipping_address
        billing = customer.billing_address
        with self.database.connection() as connection:
            connection.execute(
                """
                INSERT INTO orders (
                    order_id, customer_id, customer_name, customer_email,
                    shipping_street, shipping_city, shipping_state, shipping_postcode,
                    billing_street, billing_city, billing_state, billing_postcode,
                    payment_reference
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    order.order_id,
                    customer.customer_id,
                    customer.name,
                    customer.email,
                    shipping.street,
                    shipping.city,
                    shipping.state,
                    shipping.postcode,
                    billing.street,
                    billing.city,
                    billing.state,
                    billing.postcode,
                    order.payment_reference,
                ),
            )
            connection.executemany(
                "INSERT INTO order_items (order_id, item_id, quantity, price) VALUES (?, ?, ?, ?)",
                [
                    (order.order_id, line.item.item_id, line.quantity, f"{line.price:.2f}")
                    for line in order.items
                ],
            )

    def all(self) -> list[Order]:
        with self.database.connection() as connection:
            rows = connection.execute("SELECT * FROM orders ORDER BY created_at, order_id").fetchall()
            line_rows = {
                row["order_id"]: connection.execute(
                    "SELECT * FROM order_items WHERE order_id = ? ORDER BY item_id",
                    (row["order_id"],),
                ).fetchall()
                for row in rows
            }

        orders = []
        for row in rows:
            shipping = Address(row["shipping_street"], row["shipping_city"], row["shipping_state"], row["shipping_postcode"])
            billing = Address(row["billing_street"], row["billing_city"], row["billing_state"], row["billing_postcode"])
            customer = Customer(row["customer_id"], row["customer_name"], row["customer_email"], shipping, billing)
            cart = ShoppingCart()
            for line in line_rows[row["order_id"]]:
                item = self.items.by_isbn(line["item_id"])
                if item:
                    item.price = Decimal(line["price"])
                    cart.add_item(item, line["quantity"])
            if cart.orders:
                orders.append(Order(customer, cart.orders, row["payment_reference"], row["order_id"]))
        return orders

    def to_read_model(self) -> list[dict]:
        return [order.to_dict() for order in self.all()]


class SQLiteAnalyticsRepository:
    def __init__(self, database: SQLiteDatabase):
        self.database = database

    def get(self) -> WebsiteAnalytics:
        analytics = WebsiteAnalytics()
        with self.database.connection() as connection:
            row = connection.execute("SELECT * FROM analytics WHERE id = 1").fetchone()
            view_rows = connection.execute("SELECT * FROM analytics_item_views").fetchall()
            genre_rows = connection.execute("SELECT * FROM analytics_genre_sales").fetchall()
        if row:
            analytics.site_visits = row["site_visits"]
            analytics.revenue_total = Decimal(row["revenue_total"])
            analytics.conversion_count = row["conversion_count"]
        analytics.item_views = {row["item_id"]: row["view_count"] for row in view_rows}
        analytics.genre_sales = {row["genre"]: row["quantity"] for row in genre_rows}
        return analytics

    def save(self, analytics: WebsiteAnalytics) -> None:
        with self.database.connection() as connection:
            connection.execute(
                """
                INSERT INTO analytics (id, site_visits, revenue_total, conversion_count)
                VALUES (1, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    site_visits = excluded.site_visits,
                    revenue_total = excluded.revenue_total,
                    conversion_count = excluded.conversion_count
                """,
                (analytics.site_visits, f"{analytics.revenue_total:.2f}", analytics.conversion_count),
            )
            connection.execute("DELETE FROM analytics_item_views")
            connection.execute("DELETE FROM analytics_genre_sales")
            connection.executemany(
                "INSERT INTO analytics_item_views (item_id, view_count) VALUES (?, ?)",
                list(analytics.item_views.items()),
            )
            connection.executemany(
                "INSERT INTO analytics_genre_sales (genre, quantity) VALUES (?, ?)",
                list(analytics.genre_sales.items()),
            )


class SQLiteCustomerRepository:
    def __init__(self, database: SQLiteDatabase):
        self.database = database

    def add(self, customer: Customer, password: str) -> None:
        shipping = customer.shipping_address
        billing = customer.billing_address
        with self.database.connection() as connection:
            connection.execute(
                """
                INSERT INTO customers (
                    customer_id, name, email, password,
                    shipping_street, shipping_city, shipping_state, shipping_postcode,
                    billing_street, billing_city, billing_state, billing_postcode
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    customer.customer_id,
                    customer.name,
                    customer.email.lower(),
                    password_hash(password),
                    shipping.street,
                    shipping.city,
                    shipping.state,
                    shipping.postcode,
                    billing.street,
                    billing.city,
                    billing.state,
                    billing.postcode,
                ),
            )

    def by_email(self, email: str) -> Customer | None:
        with self.database.connection() as connection:
            row = connection.execute(
                "SELECT * FROM customers WHERE email = ?",
                (str(email or "").strip().lower(),),
            ).fetchone()
        return customer_from_row(row) if row else None

    def authenticate(self, email: str, password: str) -> Customer | None:
        raw_password = str(password or "").strip()
        with self.database.connection() as connection:
            row = connection.execute(
                "SELECT * FROM customers WHERE email = ?",
                (str(email or "").strip().lower(),),
            ).fetchone()
            if not row:
                return None
            stored_password = row["password"]
            if verify_password(stored_password, raw_password):
                if stored_password == raw_password:
                    connection.execute(
                        "UPDATE customers SET password = ? WHERE customer_id = ?",
                        (password_hash(raw_password), row["customer_id"]),
                    )
                return customer_from_row(row)
        return None


class SQLiteEmployeeRepository:
    def __init__(self, database: SQLiteDatabase):
        self.database = database

    def add(self, employee: Employee) -> None:
        with self.database.connection() as connection:
            connection.execute(
                """
                INSERT INTO employees (employee_id, name, access_code)
                VALUES (?, ?, ?)
                ON CONFLICT(employee_id) DO UPDATE SET
                    name = excluded.name,
                    access_code = excluded.access_code
                """,
                (employee.employee_id, employee.name, employee.access_code),
            )

    def by_id(self, employee_id: str) -> Employee | None:
        with self.database.connection() as connection:
            row = connection.execute(
                "SELECT * FROM employees WHERE employee_id = ?",
                (str(employee_id or "").strip(),),
            ).fetchone()
        return Employee(row["employee_id"], row["name"], row["access_code"]) if row else None


def item_values(item: Item) -> tuple:
    data = item.to_dict()
    return (
        item.item_id,
        item.item_type,
        item.name,
        f"{item.price:.2f}",
        item.stock,
        data.get("author"),
        data.get("genre"),
        data.get("edition"),
        data.get("pages"),
        data.get("cover"),
        data.get("file_format"),
        data.get("category"),
    )


def item_from_row(row) -> Item:
    raw = dict(row)
    if raw["item_type"] == "merchandise":
        return ItemFactory.create({
            "item_type": "merchandise",
            "sku": raw["item_id"],
            "name": raw["name"],
            "category": raw["category"] or raw["genre"] or "Merchandise",
            "price": raw["price"],
            "stock": raw["stock"],
        })
    return ItemFactory.create({
        "item_type": raw["item_type"],
        "isbn": raw["item_id"],
        "name": raw["name"],
        "author": raw["author"] or "",
        "genre": raw["genre"] or "",
        "edition": raw["edition"] or "",
        "pages": raw["pages"] or 0,
        "cover": raw["cover"] or 0,
        "file_format": raw["file_format"] or "EPUB",
        "price": raw["price"],
        "stock": raw["stock"],
    })


def customer_from_row(row) -> Customer:
    shipping = Address(row["shipping_street"], row["shipping_city"], row["shipping_state"], row["shipping_postcode"])
    billing = Address(row["billing_street"], row["billing_city"], row["billing_state"], row["billing_postcode"])
    return Customer(row["customer_id"], row["name"], row["email"], shipping, billing)


def password_hash(password: str) -> str:
    return generate_password_hash(str(password or "").strip())


def verify_password(stored_password: str, candidate: str) -> bool:
    if stored_password == candidate:
        return True
    try:
        return check_password_hash(stored_password, candidate)
    except ValueError:
        return False
