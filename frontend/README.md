# Frontend Hexagonal Structure

The HTML pages are thin browser adapters. They keep the existing routes, layout entry points, and Flask static serving, while reusable frontend logic lives under `frontend/`.

- `pages/`: page controllers for `index.html` and `viewCart.html`.
- `components/`: reusable UI renderers such as book cards, cart rows, order summary, toast, and empty/loading states.
- `application/`: frontend view-model logic that is independent of the DOM and HTTP.
- `adapters/http/`: the outbound HTTP adapter for existing Flask API routes.
- `shared/`: small shared helpers and constants.

This mirrors the backend hexagonal style: page controllers depend on application logic and HTTP adapters, while API calls and DOM details stay at the edges.
