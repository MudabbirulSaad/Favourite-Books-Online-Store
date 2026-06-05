async function parseJson(response, fallbackMessage) {
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.message || fallbackMessage);
  }
  return payload;
}

export const bookStoreApi = {
  async getBooks({ query = '', sort = 'original' } = {}) {
    const params = new URLSearchParams({ sort });
    if (query.trim()) params.set('q', query.trim());

    const response = await fetch(`/api/books?${params.toString()}`);
    return parseJson(response, 'Catalogue could not be loaded');
  },

  async addToCart(bookId) {
    const response = await fetch('/api/cart/items', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ book_id: bookId }),
    });
    return parseJson(response, 'Book could not be added to cart');
  },

  async getCart() {
    const response = await fetch('/api/cart');
    return parseJson(response, 'Cart could not be loaded');
  },

  async updateCartItem(isbn, quantity) {
    const response = await fetch(`/api/cart/items/${isbn}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ quantity }),
    });
    return parseJson(response, 'Cart item could not be updated');
  },

  async removeCartItem(isbn) {
    const response = await fetch(`/api/cart/items/${isbn}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
    });
    return parseJson(response, 'Cart item could not be removed');
  },

  async checkout(payload) {
    const response = await fetch('/api/checkout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return parseJson(response, 'Checkout could not be completed');
  },

  async registerCustomer(payload) {
    const response = await fetch('/api/customers', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return parseJson(response, 'Customer account could not be created');
  },

  async loginCustomer(email, password) {
    const response = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    return parseJson(response, 'Customer login failed');
  },

  async logoutCustomer() {
    const response = await fetch('/api/logout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    return parseJson(response, 'Customer logout failed');
  },

  async getSessionCustomer() {
    const response = await fetch('/api/session/customer');
    return parseJson(response, 'Customer session could not be loaded');
  },

  async addCatalogueItem(payload) {
    const response = await fetch('/api/catalogue/items', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return parseJson(response, 'Catalogue item could not be added');
  },

  async getCatalogueItem(itemId) {
    const response = await fetch(`/api/catalogue/items/${itemId}`);
    return parseJson(response, 'Catalogue item could not be loaded');
  },

  async updateCatalogueItem(itemId, payload) {
    const response = await fetch(`/api/catalogue/items/${itemId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return parseJson(response, 'Catalogue item could not be updated');
  },

  async deleteCatalogueItem(itemId, payload) {
    const response = await fetch(`/api/catalogue/items/${itemId}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return parseJson(response, 'Catalogue item could not be deleted');
  },

  async getOrders() {
    const response = await fetch('/api/orders');
    return parseJson(response, 'Orders could not be loaded');
  },

  async getAnalytics() {
    const response = await fetch('/api/analytics');
    return parseJson(response, 'Analytics could not be loaded');
  },

  async recordItemView(itemId) {
    const response = await fetch(`/api/analytics/item-views/${itemId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    return parseJson(response, 'Item view could not be recorded');
  },
};
