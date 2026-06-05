import assert from 'node:assert/strict';
import { finalTotals, orderSummary } from '../frontend/components/orderSummary.js';
import { loggedInCustomer, physicalCartSummary } from './frontend_test_helpers.mjs';

const summaryHtml = orderSummary(physicalCartSummary, loggedInCustomer);

assert.match(summaryHtml, /data-checkout-form/);
assert.doesNotMatch(summaryHtml, /name="customer.name"/);
assert.doesNotMatch(summaryHtml, /name="customer.email"/);
assert.match(summaryHtml, /Delivering To/);
assert.match(summaryHtml, /name="payment.number"/);
assert.match(summaryHtml, /placeholder="Demo: 4111111111111111"/);
assert.match(summaryHtml, /placeholder="12\/28"/);
assert.match(summaryHtml, /placeholder="123"/);
assert.doesNotMatch(summaryHtml, /name="payment.number"[^>]*value="/);
assert.doesNotMatch(summaryHtml, /name="payment.expiry"[^>]*value="/);
assert.doesNotMatch(summaryHtml, /name="payment.cvv"[^>]*value="/);
assert.match(summaryHtml, /Final Checkout Total/);
assert.match(summaryHtml, /data-final-shipping>\$3.99/);
assert.match(summaryHtml, /saad@example.com/);

assert.equal(finalTotals('21.99', '3000').total, 28.18);
assert.equal(finalTotals('21.99', '2000').total, 32.18);
assert.equal(finalTotals('9.99', '2000', false).total, 10.99);

const guestSummaryHtml = orderSummary(physicalCartSummary);

assert.match(guestSummaryHtml, /data-checkout-login-prompt/);
assert.doesNotMatch(guestSummaryHtml, /data-checkout-form/);

console.log('frontend checkout UI: ok');
