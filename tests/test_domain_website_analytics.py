from favourite_books.domain.analytics import WebsiteAnalytics
from favourite_books.domain.cart import ItemOrder
from favourite_books.domain.checkout import Order
from favourite_books.domain.customer import Address, Customer
from favourite_books.domain.items import Book


def test_website_analytics_records_visits_item_views_orders_and_genres():
    analytics = WebsiteAnalytics()
    customer = Customer.guest("Saad", "saad@example.com", Address("1 Main St", "Melbourne", "VIC", "3000"))
    book = Book(1, "The Great Gatsby", "F. Scott Fitzgerald", "Classic", "First", 180, 0, "21.99")
    order = Order(customer, [ItemOrder(book, 1)], "PAY-1")

    analytics.record_site_visit()
    analytics.record_item_view(1)
    analytics.record_order(order)

    assert analytics.to_dict()["site_visits"] == 1
    assert analytics.to_dict()["most_viewed_items"] == [1]
    assert analytics.to_dict()["most_popular_genres"] == ["Classic"]
    assert analytics.to_dict()["conversion_count"] == 1
