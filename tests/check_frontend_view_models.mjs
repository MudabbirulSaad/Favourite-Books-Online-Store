import assert from 'node:assert/strict';
import { createCatalogueViewModel } from '../frontend/application/catalogueViewModel.js';
import { createCartViewModel } from '../frontend/application/cartViewModel.js';
import { cartWithPhysicalItems, sampleBooks } from './frontend_test_helpers.mjs';

const catalogue = createCatalogueViewModel(sampleBooks);

assert.deepEqual(catalogue.getVisibleBooks().map(book => book.isbn), [2, 1]);
assert.deepEqual(catalogue.setBooks([sampleBooks[1]]).map(book => book.name), ['The Great Gatsby']);

const cart = createCartViewModel(cartWithPhysicalItems);

assert.equal(cart.isEmpty(), false);
assert.equal(cart.getSummary().total_items, 3);
assert.equal(cart.getSummary().subtotal, '63.97');

const returnedItems = cart.getItems();
returnedItems[0].quantity = 99;
assert.equal(cart.getItems()[0].quantity, 2);

assert.deepEqual(cart.setCart({ items: [], summary: { total_items: 0 } }), []);
assert.equal(cart.isEmpty(), true);
assert.deepEqual(cart.getSummary(), {
  total_items: 0,
  subtotal: '0.00',
  shipping: '0.00',
  total: '0.00',
  requires_shipping: false,
});

console.log('frontend view models: ok');
