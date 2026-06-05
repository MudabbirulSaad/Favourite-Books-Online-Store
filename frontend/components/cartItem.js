import { escapeHtml, money } from '../shared/dom.js';
import { bookCover } from './bookCover.js';

export function cartItem(item) {
  const name = escapeHtml(item.name);

  return `
    <article class="cart-item">
      ${bookCover(item, 'cart')}
      <div class="cart-item-info">
        <h2 class="cart-item-name">${name}</h2>
        <p class="cart-item-author">${escapeHtml(item.author)}</p>
        <p class="cart-item-edition">${escapeHtml(item.edition)} edition</p>
      </div>
      <div class="cart-item-actions">
        <div class="qty-control">
          <button class="qty-btn" data-change-qty="${item.isbn}" data-quantity="${item.quantity - 1}" aria-label="Decrease quantity for ${name}">
            <i class="ti ti-minus" aria-hidden="true"></i>
          </button>
          <input
            class="qty-input"
            type="number"
            min="1"
            max="20"
            value="${item.quantity}"
            aria-label="Quantity for ${name}"
            data-quantity-input="${item.isbn}"
          />
          <button class="qty-btn" data-change-qty="${item.isbn}" data-quantity="${item.quantity + 1}" aria-label="Increase quantity for ${name}">
            <i class="ti ti-plus" aria-hidden="true"></i>
          </button>
        </div>
        <div class="cart-item-price">${money(item.price * item.quantity)}</div>
        <button class="remove-btn" data-remove-item="${item.isbn}" aria-label="Remove ${name}">
          <i class="ti ti-trash" aria-hidden="true"></i>
        </button>
      </div>
    </article>`;
}
