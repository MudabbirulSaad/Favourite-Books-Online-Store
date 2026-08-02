# Favourite Books Online Store

A runnable Flask implementation of the Favourite Books online bookstore prototype for SWE30003 Assignment 3. The project builds on the Assignment 2 design and turns the catalogue, cart, checkout, customer account, employee catalogue management, order storage, and analytics flows into a working local web application.

Built by Mudabbirul Saad as a software-engineering coursework prototype.

## What This Implements

The application is intentionally small, but it is not just a static mock-up. It includes:

- A browsable catalogue for books, eBooks, and merchandise.
- Search and sorting on the catalogue page.
- Browser-session cart persistence through Flask sessions.
- Customer registration, login, logout, and session-aware checkout.
- SQLite persistence for catalogue data, customers, carts, orders, employees, and analytics.
- Payment validation through a fake payment gateway.
- Employee catalogue management for adding, editing, and deleting items.
- Recent order and analytics read models for admin evidence.
- Backend and frontend regression checks.

The cart is tied to the browser session, not the customer account. Customers can browse and add items before logging in, but checkout requires a logged-in customer so the order can use persisted customer details.

## Quick Start

From this directory:

```bash
uv sync
uv run python app.py
```

Open the site at:

```text
http://127.0.0.1:5000
```

If port `5000` is already in use, Flask will need to be run on another port. The frontend pages are served by the Flask app, so use the local server rather than opening the HTML files directly.

## Demo Credentials

Customer accounts can be created from the catalogue page. Checkout is available after registering or logging in.

For admin catalogue management:

```text
Employee ID: emp-1
Access code: staff-code
```

For successful checkout evidence, use:

```text
Card number: 4111111111111111
Expiry: 12/28
CVV: 123
```

Cards ending in `0000` are declined by the fake payment gateway. This is useful for demonstrating failed payment handling without using a real payment provider.

## Pages

- `index.html` - public catalogue page with search, sorting, account modal, and add-to-cart actions.
- `viewCart.html` - cart review and checkout page.
- `admin.html` - employee catalogue management, recent orders, and analytics evidence.

## Main API Routes

The frontend uses JSON endpoints under `/api`.

- `GET /api/catalogue` - list catalogue items.
- `POST /api/catalogue/items` - add a catalogue item with employee credentials.
- `PUT /api/catalogue/items/<item_id>` - update a catalogue item.
- `DELETE /api/catalogue/items/<item_id>` - delete a catalogue item.
- `GET /api/cart` - return the current browser-session cart.
- `POST /api/cart/items` - add an item to the cart.
- `PUT /api/cart/items/<item_id>` - update a cart quantity.
- `DELETE /api/cart/items/<item_id>` - remove an item from the cart.
- `POST /api/customers` - register a customer.
- `POST /api/login` - log in a customer and store the customer in the Flask session.
- `POST /api/logout` - log out the current customer.
- `GET /api/session/customer` - return the current logged-in customer, or `null`.
- `POST /api/checkout` - place an order for the logged-in customer.
- `GET /api/orders` - list recent stored orders.
- `GET /api/analytics` - return persisted analytics totals.
- `POST /api/analytics/item-views/<item_id>` - record a catalogue item view.

## Architecture

The code follows a small hexagonal architecture:

- `favourite_books/domain/` contains the core model: items, customer details, payment details, cart, checkout/order objects, and analytics.
- `favourite_books/application/` contains the use cases and repository protocols. This layer coordinates business operations without depending directly on Flask or SQLite details.
- `favourite_books/adapters/web/` contains the Flask app factory and HTTP route handling.
- `favourite_books/adapters/sqlite/` contains SQLite schema setup and repository implementations.
- `favourite_books/adapters/payment/` contains the fake payment gateway used for the prototype.
- `frontend/` contains modular JavaScript for API access, page behaviour, components, shared DOM helpers, and account session handling.

This keeps the assignment domain objects away from web and database concerns. The Flask layer translates HTTP input into application-service calls, and the SQLite adapter handles persistence behind repository-style interfaces.

## Persistence

The SQLite database is created automatically at:

```text
instance/favourite_books.sqlite
```

Set `BOOKSTORE_DB_PATH` to use a different database file:

```bash
BOOKSTORE_DB_PATH=instance/my_demo.sqlite uv run python app.py
```

To reset the local demo data, stop the server and delete the SQLite file in `instance/`. The next run will recreate the schema and seed the demo catalogue and employee account.

Runtime data, logs, virtual environments, caches, and local secrets are ignored by Git.

## Checkout Flow

The checkout flow is account-aware:

1. A visitor can browse the catalogue and add items to the browser-session cart.
2. Checkout is blocked until the visitor registers or logs in.
3. The backend session is treated as the authority for the logged-in customer.
4. The order uses the persisted customer name, email, and address.
5. The request sends payment details only.
6. Payment is authorised by the fake gateway.
7. On success, the order is stored, stock is decremented, analytics are updated, and the cart is cleared.
8. On failure, the cart and stock are preserved.

Shipping is calculated only when needed. eBook-only carts do not receive shipping charges. Physical books and merchandise require shipping.

## Validation

The backend validates user input before updating state. Examples include:

- Customer email format, duplicate email checks, password length, and address fields.
- Positive cart quantities with reasonable limits.
- Supported catalogue item types.
- Positive ISBN/SKU values.
- Non-empty item names and required item-specific fields.
- Price greater than zero and stock greater than or equal to zero.
- Payment card number, expiry, and CVV format.

The frontend also keeps required fields visible and uses placeholders for demo payment details instead of pre-filled values.

## Tests

Run the Python test suite:

```bash
uv run pytest -q
```

Run the frontend checks:

```bash
npm test
```

The tests cover API flows, domain models, service behaviour, SQLite persistence, cart read models, order and analytics read models, frontend view models, checkout UI expectations, and frontend module syntax/contracts.

## Project Layout

```text
.
├── app.py
├── admin.html
├── index.html
├── viewCart.html
├── style.css
├── favourite_books/
│   ├── adapters/
│   │   ├── payment/
│   │   ├── sqlite/
│   │   └── web/
│   ├── application/
│   ├── domain/
│   └── bootstrap.py
├── frontend/
│   ├── adapters/
│   ├── application/
│   ├── components/
│   ├── pages/
│   └── shared/
└── tests/
```

## Development Notes

This is an assignment prototype, so the payment gateway and employee access code are deliberately simple. The structure leaves room for replacing them with real adapters later without changing the core domain model or the application service contracts.

The most important behaviour to preserve is that successful business operations persist through SQLite, while temporary browsing/cart state remains scoped to the current browser session.
