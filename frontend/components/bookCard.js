import { escapeHtml, money } from '../shared/dom.js';
import { bookCover } from './bookCover.js';

export function bookCard(book, index) {
  return `
    <article class="book-card" id="bookCard-${index}">
      ${bookCover(book, 'full', true)}
      <div class="book-info">
        <div>
          <h2 class="book-name">${escapeHtml(book.name)}</h2>
          <p class="book-author">by ${escapeHtml(book.author)}</p>
        </div>
        <div class="book-meta">
          <span class="meta-pill"><i class="ti ti-book" aria-hidden="true"></i>${escapeHtml(book.edition)} ed.</span>
          <span class="meta-pill"><i class="ti ti-file-text" aria-hidden="true"></i>${book.pages} pages</span>
          <span class="meta-pill"><i class="ti ti-tag" aria-hidden="true"></i>${escapeHtml(book.genre)}</span>
        </div>
      </div>
      <div class="card-footer">
        <span class="book-price">${money(book.price)}</span>
        <button class="primary-action" data-add-to-cart="${book.isbn}">
          <i class="ti ti-shopping-cart-plus" aria-hidden="true"></i>
          Add to Cart
        </button>
      </div>
    </article>`;
}
