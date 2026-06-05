from decimal import Decimal

from favourite_books.domain.checkout import Order


class WebsiteAnalytics:
    """Simple analytics object from the Assignment 2 design."""

    def __init__(self):
        self.site_visits = 0
        self.item_views: dict[int, int] = {}
        self.genre_sales: dict[str, int] = {}
        self.revenue_total = Decimal("0.00")
        self.conversion_count = 0

    def record_site_visit(self) -> None:
        self.site_visits += 1

    def record_item_view(self, item_id: int) -> None:
        self.item_views[item_id] = self.item_views.get(item_id, 0) + 1

    def record_order(self, order: Order) -> None:
        self.conversion_count += 1
        self.revenue_total += order.total
        for line in order.items:
            genre = getattr(line.item, "genre", getattr(line.item, "category", "General"))
            self.genre_sales[genre] = self.genre_sales.get(genre, 0) + line.quantity

    def most_viewed_items(self) -> list[int]:
        return sorted(self.item_views, key=self.item_views.get, reverse=True)

    def most_popular_genres(self) -> list[str]:
        return sorted(self.genre_sales, key=self.genre_sales.get, reverse=True)

    def to_dict(self) -> dict:
        return {
            "site_visits": self.site_visits,
            "most_viewed_items": self.most_viewed_items(),
            "most_popular_genres": self.most_popular_genres(),
            "revenue_total": f"{self.revenue_total:.2f}",
            "conversion_count": self.conversion_count,
        }
