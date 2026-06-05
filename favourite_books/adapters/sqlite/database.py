from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    item_id INTEGER PRIMARY KEY,
    item_type TEXT NOT NULL,
    name TEXT NOT NULL,
    price TEXT NOT NULL,
    stock INTEGER NOT NULL,
    author TEXT,
    genre TEXT,
    edition TEXT,
    pages INTEGER,
    cover INTEGER,
    file_format TEXT,
    category TEXT
);

CREATE TABLE IF NOT EXISTS carts (
    cart_id TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS cart_items (
    cart_id TEXT NOT NULL,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    PRIMARY KEY (cart_id, item_id),
    FOREIGN KEY (cart_id) REFERENCES carts(cart_id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES items(item_id)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    customer_name TEXT NOT NULL,
    customer_email TEXT NOT NULL,
    shipping_street TEXT NOT NULL,
    shipping_city TEXT NOT NULL,
    shipping_state TEXT NOT NULL,
    shipping_postcode TEXT NOT NULL,
    billing_street TEXT NOT NULL,
    billing_city TEXT NOT NULL,
    billing_state TEXT NOT NULL,
    billing_postcode TEXT NOT NULL,
    payment_reference TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    order_id TEXT NOT NULL,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price TEXT NOT NULL,
    PRIMARY KEY (order_id, item_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES items(item_id)
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    shipping_street TEXT NOT NULL,
    shipping_city TEXT NOT NULL,
    shipping_state TEXT NOT NULL,
    shipping_postcode TEXT NOT NULL,
    billing_street TEXT NOT NULL,
    billing_city TEXT NOT NULL,
    billing_state TEXT NOT NULL,
    billing_postcode TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS employees (
    employee_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    access_code TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS analytics (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    site_visits INTEGER NOT NULL,
    revenue_total TEXT NOT NULL,
    conversion_count INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS analytics_item_views (
    item_id INTEGER PRIMARY KEY,
    view_count INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS analytics_genre_sales (
    genre TEXT PRIMARY KEY,
    quantity INTEGER NOT NULL
);
"""


class SQLiteDatabase:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._active_connection: sqlite3.Connection | None = None

    def initialise(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as connection:
            connection.executescript(SCHEMA)
            connection.execute(
                "INSERT OR IGNORE INTO analytics (id, site_visits, revenue_total, conversion_count) VALUES (1, 0, '0.00', 0)"
            )

    @contextmanager
    def connection(self):
        if self._active_connection is not None:
            yield self._active_connection
            return

        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @contextmanager
    def transaction(self):
        if self._active_connection is not None:
            yield
            return

        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        self._active_connection = connection
        try:
            connection.execute("BEGIN IMMEDIATE")
            yield
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            self._active_connection = None
            connection.close()
