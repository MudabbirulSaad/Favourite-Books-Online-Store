import { bookStoreApi } from '../adapters/http/bookStoreApi.js';
import { createCartViewModel } from '../application/cartViewModel.js';
import { cartItem } from '../components/cartItem.js';
import { emptyState } from '../components/states.js';
import { finalTotals, orderSummary } from '../components/orderSummary.js';
import { createToast } from '../components/toast.js';
import { clearCustomer, getStoredCustomer, storeCustomer } from '../shared/accountSession.js';
import { initAccountModal } from '../shared/accountModal.js';
import { byId } from '../shared/dom.js';

const toast = createToast();
const cart = createCartViewModel();
let currentCustomer = getStoredCustomer();
const accountModal = initAccountModal({
  toast,
  onAccountChange(customer) {
    currentCustomer = customer;
    renderCart();
  },
});

function displayEmptyCart() {
  return emptyState(
    'ti-shopping-cart-off',
    'Your cart is empty',
    'Add a book from the catalogue before checkout.',
    `<a class="primary-action empty-cart-link" href="index.html">
      <i class="ti ti-arrow-left" aria-hidden="true"></i> Browse books
    </a>`
  );
}

function renderCart() {
  const container = byId('cart-container');

  if (cart.isEmpty()) {
    container.innerHTML = displayEmptyCart();
    return;
  }

  const cartItems = cart.getItems();
  container.innerHTML = `
    <div class="cart-list">${cartItems.map(cartItem).join('')}</div>
    ${orderSummary(cart.getSummary(), currentCustomer)}
  `;
  updateFinalCheckoutTotal();
}

async function loadCart() {
  const container = byId('cart-container');

  try {
    const [cartReadModel, sessionCustomer] = await Promise.all([
      bookStoreApi.getCart(),
      bookStoreApi.getSessionCustomer(),
    ]);
    currentCustomer = sessionCustomer;
    if (sessionCustomer) {
      storeCustomer(sessionCustomer);
    } else {
      clearCustomer();
    }
    accountModal.render();
    cart.setCart(cartReadModel);
    renderCart();
  } catch {
    container.innerHTML = emptyState(
      'ti-alert-circle',
      'Cart could not be loaded',
      'Please refresh the page and try again.'
    );
  }
}

async function changeQty(isbn, quantity) {
  try {
    const result = await bookStoreApi.updateCartItem(Number(isbn), quantity);
    toast.show(result.message);
    loadCart();
  } catch (error) {
    toast.show(error.message);
  }
}

async function removeItem(isbn) {
  try {
    const result = await bookStoreApi.removeCartItem(Number(isbn));
    toast.show(result.message);
    loadCart();
  } catch (error) {
    toast.show(error.message);
  }
}

async function checkout() {
  try {
    const result = await bookStoreApi.checkout(checkoutPayload());
    toast.show(result.message);
    loadCart();
  } catch (error) {
    toast.show(error.message);
  }
}

function checkoutPayload() {
  const form = byId('cart-container').querySelector('[data-checkout-form]');
  const data = new FormData(form);

  return {
    payment: {
      cardholder: data.get('payment.cardholder'),
      number: data.get('payment.number'),
      expiry: data.get('payment.expiry'),
      cvv: data.get('payment.cvv'),
    },
  };
}

function updateFinalCheckoutTotal() {
  const form = byId('cart-container').querySelector('[data-checkout-form]');
  if (!form) return;

  const summary = cart.getSummary();
  const totals = finalTotals(
    summary.subtotal,
    currentCustomer?.shipping_address?.postcode || '',
    summary.requires_shipping
  );
  const shippingElement = form.closest('.order-summary').querySelector('[data-final-shipping]');
  const taxElement = form.closest('.order-summary').querySelector('[data-tax-total]');
  const totalElement = form.closest('.order-summary').querySelector('[data-final-total]');
  shippingElement.textContent = `$${totals.shipping.toFixed(2)}`;
  taxElement.textContent = `$${totals.tax.toFixed(2)}`;
  totalElement.textContent = `$${totals.total.toFixed(2)}`;
}

function bindEvents() {
  byId('cart-container').addEventListener('click', event => {
    const quantityButton = event.target.closest('[data-change-qty]');
    if (quantityButton) {
      changeQty(quantityButton.dataset.changeQty, quantityButton.dataset.quantity);
      return;
    }

    const removeButton = event.target.closest('[data-remove-item]');
    if (removeButton) {
      removeItem(removeButton.dataset.removeItem);
      return;
    }

    if (event.target.closest('[data-checkout]')) {
      event.preventDefault();
      checkout();
    }
  });

  byId('cart-container').addEventListener('submit', event => {
    if (!event.target.closest('[data-checkout-form]')) return;
    event.preventDefault();
    checkout();
  });

  byId('cart-container').addEventListener('change', event => {
    const input = event.target.closest('[data-quantity-input]');
    if (input) {
      changeQty(input.dataset.quantityInput, input.value);
    }
  });
}

bindEvents();
loadCart();
