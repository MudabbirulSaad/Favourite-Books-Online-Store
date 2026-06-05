import assert from 'node:assert/strict';
import { readProjectFile } from './frontend_test_helpers.mjs';

const apiSource = readProjectFile('../frontend/adapters/http/bookStoreApi.js');
assert.match(apiSource, /getCatalogueItem/);
assert.match(apiSource, /updateCatalogueItem/);
assert.match(apiSource, /deleteCatalogueItem/);
assert.match(apiSource, /registerCustomer/);
assert.match(apiSource, /loginCustomer/);
assert.match(apiSource, /logoutCustomer/);
assert.match(apiSource, /getSessionCustomer/);
assert.match(apiSource, /recordItemView/);

const cartPageSource = readProjectFile('../frontend/pages/cartPage.js');
assert.doesNotMatch(cartPageSource, /customer: \{/);
assert.match(cartPageSource, /getSessionCustomer/);

const adminSource = readProjectFile('../frontend/pages/adminPage.js');
assert.match(adminSource, /loadAdminData/);
assert.match(adminSource, /data-edit-item/);
assert.match(adminSource, /data-delete-item/);
assert.match(adminSource, /renderInsights/);

const adminHtml = readProjectFile('../admin.html');
assert.match(adminHtml, /name="access_code" type="password"/);

const accountSource = readProjectFile('../frontend/shared/accountSession.js');
assert.match(accountSource, /sessionStorage/);

const cataloguePageSource = readProjectFile('../frontend/pages/cataloguePage.js');
assert.match(cataloguePageSource, /initAccountModal/);

const accountModalSource = readProjectFile('../frontend/shared/accountModal.js');
assert.match(accountModalSource, /Login \/ Register/);
assert.match(accountModalSource, /escapeHtml\(customer\.name\)/);
assert.match(accountModalSource, /escapeHtml\(customer\.email\)/);
assert.match(accountModalSource, /onAccountChange/);

console.log('frontend contracts: ok');
