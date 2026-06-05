from favourite_books.domain.analytics import WebsiteAnalytics
from favourite_books.domain.cart import ItemOrder
from favourite_books.domain.checkout import Order
from favourite_books.domain.customer import Address, Customer
from favourite_books.domain.items import Book


def test_order_history_and_analytics_repositories_expose_read_models(sqlite_repositories):
    orders = sqlite_repositories["orders"]
    customer = Customer.guest("Saad", "saad@example.com", Address("1 Main St", "Melbourne", "VIC", "3000"))
    book = Book(1, "The Great Gatsby", "F. Scott Fitzgerald", "Classic", "First", 180, 0, "21.99")
    sqlite_repositories["books"].add(book)
    orders.add(Order(customer, [ItemOrder(book, 1)], "PAY-1"))
    analytics = WebsiteAnalytics()

    analytics.record_order(orders.all()[0])
    sqlite_repositories["analytics"].save(analytics)

    assert orders.to_read_model()[0]["customer"]["email"] == "saad@example.com"
    assert sqlite_repositories["analytics"].get().to_dict()["conversion_count"] == 1
