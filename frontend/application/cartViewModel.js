const emptySummary = {
  total_items: 0,
  subtotal: '0.00',
  shipping: '0.00',
  total: '0.00',
  requires_shipping: false,
};

export function createCartViewModel(initialCart = { items: [], summary: emptySummary }) {
  let items = cloneItems(initialCart.items || []);
  let summary = { ...emptySummary, ...(initialCart.summary || {}) };

  function setCart(nextCart) {
    items = cloneItems(nextCart.items || []);
    summary = { ...emptySummary, ...(nextCart.summary || {}) };
    return getItems();
  }

  function getItems() {
    return cloneItems(items);
  }

  function isEmpty() {
    return items.length === 0;
  }

  function getSummary() {
    return { ...summary };
  }

  return {
    setCart,
    getItems,
    getSummary,
    isEmpty,
  };
}

function cloneItems(items) {
  return items.map(item => ({ ...item }));
}
