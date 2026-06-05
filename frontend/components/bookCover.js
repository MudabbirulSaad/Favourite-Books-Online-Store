import { coverFor } from '../shared/coverPalette.js';
import { escapeHtml } from '../shared/dom.js';

export function bookCover(book, variant = 'full', includeGenre = false) {
  const cover = coverFor(book);

  return `
    <div class="book-cover book-cover--${variant}" style="background:${cover.bg}">
      ${includeGenre ? `<span class="badge-genre">${escapeHtml(book.genre)}</span>` : ''}
      <div class="cover-art cover-art--${variant}" style="background:${cover.bg}; border-left:4px solid ${cover.accent}" aria-hidden="true">
        <div class="cover-spine"></div>
        <div class="cover-title" style="color:${cover.accent}">${escapeHtml(book.name)}</div>
        <div class="cover-author">${escapeHtml(book.author)}</div>
      </div>
    </div>`;
}
