const STORAGE_KEY = 'favouriteBooks.customer';

export function getStoredCustomer() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function storeCustomer(customer) {
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(customer));
}

export function clearCustomer() {
  sessionStorage.removeItem(STORAGE_KEY);
}
