from favourite_books.adapters.web.flask_app import create_app
from favourite_books.bootstrap import build_services

catalogue_service, cart_service, customer_service, order_repository, analytics_repository = build_services()
app = create_app(
    catalogue_service,
    cart_service,
    customer_service,
    order_repository,
    analytics_repository,
)


if __name__ == "__main__":
    print("Bookstore running at http://127.0.0.1:5000")
    app.run(debug=True, use_reloader=False)
