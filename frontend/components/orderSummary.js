import { escapeHtml, money } from '../shared/dom.js';

export function orderSummary(summary, customer = null) {
  const address = customer?.shipping_address || {};
  const postcode = address.postcode || '';
  const final = finalTotals(summary.subtotal, postcode, summary.requires_shipping);

  return `
    <aside class="order-summary" aria-label="Order summary">
      <h2 class="summary-title">Order Summary</h2>
      <div class="summary-row">
        <span class="summary-label">${summary.total_items} item${summary.total_items !== 1 ? 's' : ''}</span>
        <span class="summary-value">${money(summary.subtotal)}</span>
      </div>
      <div class="summary-row">
        <span class="summary-label">Shipping</span>
        <span class="summary-value">${money(summary.shipping)}</span>
      </div>
      <div class="summary-divider"></div>
      <div class="summary-row summary-total">
        <span>Cart Estimate</span>
        <span>${money(summary.total)}</span>
      </div>
      <div class="summary-row">
        <span class="summary-label">Final Shipping</span>
        <span class="summary-value" data-final-shipping>${money(final.shipping)}</span>
      </div>
      <div class="summary-row">
        <span class="summary-label">Tax</span>
        <span class="summary-value" data-tax-total>${money(final.tax)}</span>
      </div>
      <div class="summary-row summary-total">
        <span>Final Checkout Total</span>
        <span data-final-total>${money(final.total)}</span>
      </div>
      ${customer ? paymentForm(customer) : checkoutLoginPrompt()}
    </aside>`;
}

export function finalTotals(subtotalValue, postcode = '', requiresShipping = true) {
  const subtotal = Number(subtotalValue);
  const shipping = requiresShipping ? (String(postcode).startsWith('3') ? 3.99 : 7.99) : 0;
  const tax = Number((subtotal * 0.10).toFixed(2));
  return {
    shipping,
    tax,
    total: Number((subtotal + shipping + tax).toFixed(2)),
  };
}

function paymentForm(customer) {
  const address = customer.shipping_address || {};
  const deliveryLine = [
    address.street,
    address.city,
    address.state,
    address.postcode,
  ].filter(Boolean).join(', ');

  return `
    <div class="delivery-summary">
      <h3 class="checkout-title">Delivering To</h3>
      <strong>${escapeHtml(customer.name)}</strong>
      <span>${escapeHtml(customer.email)}</span>
      <span>${escapeHtml(deliveryLine)}</span>
    </div>
    <form class="checkout-form" data-checkout-form>
      <h3 class="checkout-title">Payment Details</h3>
      <label class="checkout-field">
        <span>Cardholder</span>
        <input name="payment.cardholder" autocomplete="cc-name" required value="${escapeAttribute(customer.name)}" />
      </label>
      <label class="checkout-field">
        <span>Card Number</span>
        <input name="payment.number" inputmode="numeric" autocomplete="cc-number" required placeholder="Demo: 4111111111111111" />
      </label>
      <div class="checkout-grid">
        <label class="checkout-field">
          <span>Expiry</span>
          <input name="payment.expiry" autocomplete="cc-exp" required placeholder="12/28" />
        </label>
        <label class="checkout-field">
          <span>CVV</span>
          <input name="payment.cvv" inputmode="numeric" autocomplete="cc-csc" required placeholder="123" />
        </label>
      </div>
      <button class="checkout-btn" type="submit" data-checkout>
        <i class="ti ti-credit-card" aria-hidden="true"></i> Checkout
      </button>
    </form>`;
}

function checkoutLoginPrompt() {
  return `
    <div class="checkout-login-prompt" data-checkout-login-prompt>
      <h3 class="checkout-title">Login Required</h3>
      <p>Login or register before placing this order.</p>
      <a class="primary-action" href="index.html#accountPanel">
        <i class="ti ti-user-circle" aria-hidden="true"></i> Account
      </a>
    </div>`;
}

function escapeAttribute(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('"', '&quot;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;');
}
