import { createCatalogueViewModel } from '../application/catalogueViewModel.js';
import { bookStoreApi } from '../adapters/http/bookStoreApi.js';
import { bookCard } from '../components/bookCard.js';
import { emptyState } from '../components/states.js';
import { createToast } from '../components/toast.js';
import { initAccountModal } from '../shared/accountModal.js';
import { byId } from '../shared/dom.js';

const toast = createToast();
let catalogue;
let searchActive = false;
let activeQuery = '';
let activeSort = 'original';
const accountModal = initAccountModal({ toast });

function renderCards() {
  const homeView = byId('homeView');
  const books = catalogue.getVisibleBooks();

  if (books.length === 0) {
    homeView.innerHTML = emptyState('ti-book-off', 'No matching books', 'Try another title or author.');
    return;
  }

  homeView.innerHTML = books.map(bookCard).join('');
  books.forEach(book => {
    void bookStoreApi.recordItemView(book.isbn).catch(() => {});
  });
}

function toggleSearch() {
  searchActive = !searchActive;
  const searchBar = byId('searchBar');
  searchBar.classList.toggle('open', searchActive);

  if (searchActive) {
    byId('searchInput').focus();
    return;
  }

  byId('searchInput').value = '';
  activeQuery = '';
  loadBooks();
}

async function handleAddToCart(bookId) {
  try {
    const result = await bookStoreApi.addToCart(Number(bookId));
    toast.show(result.message);
  } catch (error) {
    toast.show(error.message);
  }
}

async function loadBooks() {
  try {
    const books = await bookStoreApi.getBooks({ query: activeQuery, sort: activeSort });
    catalogue.setBooks(books);
    renderCards();
  } catch (error) {
    toast.show(error.message);
  }
}

function bindEvents() {
  byId('searchToggle').addEventListener('click', toggleSearch);
  byId('searchClose').addEventListener('click', toggleSearch);
  byId('searchInput').addEventListener('input', async event => {
    activeQuery = event.target.value;
    await loadBooks();
  });

  byId('sortToggle').addEventListener('click', () => {
    byId('sortMenu').classList.toggle('open');
  });

  byId('sortMenu').addEventListener('click', event => {
    const sortButton = event.target.closest('[data-sort]');
    if (!sortButton) return;

    const sortBy = sortButton.dataset.sort;
    byId('sortMenu').classList.remove('open');
    activeSort = sortBy;
    void loadBooks();
    toast.show(`Sorted by ${sortBy}`);
  });

  byId('homeView').addEventListener('click', event => {
    const addButton = event.target.closest('[data-add-to-cart]');
    if (!addButton) return;
    handleAddToCart(addButton.dataset.addToCart);
  });

  document.addEventListener('click', event => {
    const menu = byId('sortMenu');
    if (!event.target.closest('.sort-dropdown')) menu.classList.remove('open');
  });
}

async function initCataloguePage() {
  try {
    catalogue = createCatalogueViewModel(await bookStoreApi.getBooks({ sort: activeSort }));
    renderCards();
    await accountModal.refresh();
    bindEvents();
    if (window.location.hash === '#accountPanel') {
      accountModal.open();
    }
  } catch {
    byId('homeView').innerHTML = emptyState(
      'ti-alert-circle',
      'Catalogue could not be loaded',
      'Please refresh the page and try again.'
    );
  }
}

initCataloguePage();
