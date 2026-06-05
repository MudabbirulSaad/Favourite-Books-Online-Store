export function createCatalogueViewModel(initialBooks = []) {
  let visibleBooks = cloneBooks(initialBooks);

  function getVisibleBooks() {
    return cloneBooks(visibleBooks);
  }

  function setBooks(nextBooks) {
    visibleBooks = cloneBooks(nextBooks);
    return getVisibleBooks();
  }

  return {
    getVisibleBooks,
    setBooks,
  };
}

function cloneBooks(books) {
  return books.map(book => ({ ...book }));
}
