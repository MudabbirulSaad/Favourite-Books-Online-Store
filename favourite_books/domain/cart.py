from decimal import Decimal

from favourite_books.domain.items import Item, TangibleItem


class InvalidQuantityError(Exception):
    """Raised when a cart item quantity violates the domain invariant."""


class ItemOrder:
    """One cart line item linking an item with quantity and price."""

    MAX_QUANTITY = 20

    def __init__(self, item: Item, quantity: int):
        self.item = item
        self.book = item
        self.price = item.get_price()
        self.update_quantity(quantity)

    def update_quantity(self, quantity: int) -> None:
        if quantity < 1:
            raise InvalidQuantityError("Quantity must be at least 1.")
        if quantity > self.MAX_QUANTITY:
            raise InvalidQuantityError("Quantity cannot exceed 20.")
        self.quantity = quantity

    def line_total(self) -> Decimal:
        return self.price * self.quantity

    @property
    def requires_shipping(self) -> bool:
        return isinstance(self.item, TangibleItem)

    def to_dict(self) -> dict:
        return {
            **self.item.to_dict(),
            "quantity": self.quantity,
            "line_total": f"{self.line_total():.2f}",
        }


class ShoppingCart:
    """Session-style shopping cart from the Assignment 2 design."""

    def __init__(self):
        self.orders: list[ItemOrder] = []

    def add_item(self, item: Item, quantity: int = 1) -> None:
        existing = self.get_item(item.item_id)
        if existing:
            existing.update_quantity(existing.quantity + quantity)
            return
        self.orders.append(ItemOrder(item, quantity))

    def get_item(self, item_id: int) -> ItemOrder | None:
        return next((order for order in self.orders if order.item.item_id == item_id), None)

    def update_quantity(self, item_id: int, quantity: int) -> bool:
        item = self.get_item(item_id)
        if not item:
            return False
        item.update_quantity(quantity)
        return True

    def remove_item(self, item_id: int) -> bool:
        before = len(self.orders)
        self.orders = [order for order in self.orders if order.item.item_id != item_id]
        return len(self.orders) < before

    def clear(self) -> None:
        self.orders.clear()

    def total_items(self) -> int:
        return sum(order.quantity for order in self.orders)

    def subtotal(self) -> Decimal:
        return sum((order.line_total() for order in self.orders), Decimal("0.00"))

    def to_list(self) -> list[dict]:
        return [order.to_dict() for order in self.orders]
