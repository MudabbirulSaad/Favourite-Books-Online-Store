import os
import secrets

from flask import Flask, jsonify, request, send_from_directory, session
from flask_cors import CORS
from pathlib import Path

from favourite_books.application.services import (
    AnalyticsRepository,
    CartService,
    CatalogueService,
    CustomerService,
    NotFoundError,
    OrderRepository,
    ValidationError,
)

SESSION_CUSTOMER_EMAIL = "customer_email"


def create_app(
    catalogue_service: CatalogueService,
    cart_service: CartService,
    customer_service: CustomerService | None = None,
    order_repository: OrderRepository | None = None,
    analytics_repository: AnalyticsRepository | None = None,
) -> Flask:
    web_root = Path(__file__).resolve().parents[3]
    app = Flask(__name__, static_folder=None)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-me")
    CORS(
        app,
        resources={
            r"/api/*": {"origins": ["http://127.0.0.1:5000", "http://localhost:5000"]},
        },
    )

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return message_response(str(error), 400)

    @app.errorhandler(NotFoundError)
    def handle_not_found_error(error):
        return message_response(str(error), 404)

    def current_customer():
        email = session.get(SESSION_CUSTOMER_EMAIL)
        if not email or not customer_service:
            return None
        customer = customer_service.by_email(email)
        if not customer:
            session.pop(SESSION_CUSTOMER_EMAIL, None)
        return customer

    @app.route("/")
    def index():
        return send_from_directory(web_root, "index.html")

    @app.route("/index.html")
    def index_file():
        return send_from_directory(web_root, "index.html")

    @app.route("/viewCart.html")
    def cart_page():
        return send_from_directory(web_root, "viewCart.html")

    @app.route("/admin.html")
    def admin_page():
        return send_from_directory(web_root, "admin.html")

    @app.route("/style.css")
    def stylesheet():
        return send_from_directory(web_root, "style.css")

    @app.route("/frontend/<path:asset_path>")
    def frontend_asset(asset_path: str):
        return send_from_directory(web_root / "frontend", asset_path)

    @app.route("/api/books", methods=["GET"])
    def get_books():
        sort = request.args.get("sort", "original")
        query = request.args.get("q", "")
        books = catalogue_service.list_books(sort=sort, query=query)
        return jsonify([book.to_dict() for book in books])

    @app.route("/api/catalogue/items", methods=["POST"])
    def add_catalogue_item():
        data = request.get_json(silent=True) or {}
        result = catalogue_service.add_catalogue_item(
            data.get("employee_id", ""),
            data.get("access_code", ""),
            data.get("item", {}),
        )
        return jsonify(result), 201

    @app.route("/api/catalogue/items/<item_id>", methods=["GET"])
    def get_catalogue_item(item_id):
        item_id = parse_positive_int(item_id, "Item ID")
        return jsonify(catalogue_service.get_catalogue_item(item_id))

    @app.route("/api/catalogue/items/<item_id>", methods=["PATCH"])
    def update_catalogue_item(item_id):
        item_id = parse_positive_int(item_id, "Item ID")
        data = request.get_json(silent=True) or {}
        return jsonify(catalogue_service.update_catalogue_item(
            item_id,
            data.get("employee_id", ""),
            data.get("access_code", ""),
            data.get("item", {}),
        ))

    @app.route("/api/catalogue/items/<item_id>", methods=["DELETE"])
    def delete_catalogue_item(item_id):
        item_id = parse_positive_int(item_id, "Item ID")
        data = request.get_json(silent=True) or {}
        return jsonify(catalogue_service.delete_catalogue_item(
            item_id,
            data.get("employee_id", ""),
            data.get("access_code", ""),
        ))

    @app.route("/api/customers", methods=["POST"])
    def register_customer():
        if not customer_service:
            raise ValidationError("Customer registration is not configured.")
        customer = customer_service.register_customer(request.get_json(silent=True) or {})
        session[SESSION_CUSTOMER_EMAIL] = customer["email"]
        return jsonify(customer), 201

    @app.route("/api/login", methods=["POST"])
    def login():
        if not customer_service:
            raise ValidationError("Customer login is not configured.")
        data = request.get_json(silent=True) or {}
        customer = customer_service.login(data.get("email", ""), data.get("password", ""))
        session[SESSION_CUSTOMER_EMAIL] = customer["email"]
        return jsonify(customer)

    @app.route("/api/logout", methods=["POST"])
    def logout():
        session.pop(SESSION_CUSTOMER_EMAIL, None)
        return message_response("Logged out.")

    @app.route("/api/session/customer", methods=["GET"])
    def session_customer():
        return jsonify(current_customer().to_dict() if current_customer() else None)

    @app.route("/api/orders", methods=["GET"])
    def orders():
        if not order_repository or not hasattr(order_repository, "to_read_model"):
            raise ValidationError("Order history is not configured.")
        return jsonify(order_repository.to_read_model())

    @app.route("/api/analytics", methods=["GET"])
    def analytics():
        if not analytics_repository:
            raise ValidationError("Analytics are not configured.")
        return jsonify(analytics_repository.get().to_dict())

    @app.route("/api/analytics/item-views/<item_id>", methods=["POST"])
    def record_item_view(item_id):
        item_id = parse_positive_int(item_id, "Item ID")
        return jsonify(catalogue_service.record_item_view(item_id))

    @app.route("/api/cart/items", methods=["POST"])
    def add_cart_item():
        data = request.get_json(silent=True) or {}
        book_id = parse_positive_int(data.get("book_id"), "Book ID")
        return message_response(cart_service.add_book(current_cart_id(), book_id))

    @app.route("/api/cart", methods=["GET"])
    def get_cart():
        return jsonify(cart_service.get_cart_read_model(current_cart_id()))

    @app.route("/api/cart/items/<isbn>", methods=["DELETE"])
    def remove_cart_item(isbn):
        isbn = parse_positive_int(isbn, "ISBN")
        return message_response(cart_service.remove_item(current_cart_id(), isbn))

    @app.route("/api/cart/items/<isbn>", methods=["PATCH"])
    def update_cart_item(isbn):
        data = request.get_json(silent=True) or {}
        isbn = parse_positive_int(isbn, "ISBN")
        quantity = parse_positive_int(data.get("quantity"), "Quantity")
        return message_response(cart_service.update_quantity(current_cart_id(), isbn, quantity))

    @app.route("/api/checkout", methods=["POST"])
    def checkout():
        customer = current_customer()
        if not customer:
            return message_response("Login is required before checkout.", 401)
        data = request.get_json(silent=True) or {}
        result = cart_service.checkout(
            current_cart_id(),
            customer,
            data.get("payment", {}),
        )
        return jsonify(result)

    return app


def current_cart_id() -> str:
    if "cart_id" not in session:
        session["cart_id"] = secrets.token_urlsafe(16)
    return session["cart_id"]


def parse_positive_int(value, field_name: str) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{field_name} must be a whole number.") from exc
    if parsed < 1:
        raise ValidationError(f"{field_name} must be at least 1.")
    return parsed


def message_response(message: str, status: int = 200):
    return jsonify({"message": message}), status
