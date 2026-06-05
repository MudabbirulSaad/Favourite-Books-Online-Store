import { bookStoreApi } from '../adapters/http/bookStoreApi.js';
import { createToast } from '../components/toast.js';
import { byId, escapeHtml, money } from '../shared/dom.js';

const toast = createToast();
const form = byId('catalogue-form');
const output = byId('admin-output');
const table = byId('catalogue-table');
const formTitle = byId('form-title');
const insights = byId('admin-insights');

let catalogue = [];

form.addEventListener('submit', async event => {
  event.preventDefault();
  const data = new FormData(form);
  const item = buildItem(data);
  const credentials = {
    employee_id: data.get('employee_id'),
    access_code: data.get('access_code'),
  };
  const editingId = data.get('editing_id');

  try {
    const result = editingId
      ? await bookStoreApi.updateCatalogueItem(editingId, { ...credentials, item })
      : await bookStoreApi.addCatalogueItem({ ...credentials, item });
    toast.show(result.message);
    output.innerHTML = `<pre>${escapeHtml(JSON.stringify(result.item, null, 2))}</pre>`;
    resetForm(false);
    await loadAdminData();
  } catch (error) {
    toast.show(error.message);
  }
});

byId('reset-form').addEventListener('click', () => resetForm(true));

table.addEventListener('click', async event => {
  const editButton = event.target.closest('[data-edit-item]');
  const deleteButton = event.target.closest('[data-delete-item]');

  if (editButton) {
    await loadItemIntoForm(editButton.dataset.editItem);
    return;
  }

  if (deleteButton) {
    await deleteItem(deleteButton.dataset.deleteItem);
  }
});

function buildItem(data) {
  const type = data.get('item_type');
  const identifier = Number(data.get('identifier'));
  const base = {
    item_type: type,
    name: data.get('name'),
    price: data.get('price'),
    stock: Number(data.get('stock') || 0),
  };

  if (type === 'merchandise') {
    return {
      ...base,
      sku: identifier,
      category: data.get('genre'),
    };
  }

  return {
    ...base,
    isbn: identifier,
    author: data.get('author'),
    genre: data.get('genre'),
    edition: data.get('edition') || 'First',
    pages: Number(data.get('pages') || 0),
    file_format: type === 'ebook' ? 'EPUB' : undefined,
  };
}

async function loadAdminData() {
  const [items, orders, analytics] = await Promise.all([
    bookStoreApi.getBooks({ sort: 'original' }),
    bookStoreApi.getOrders(),
    bookStoreApi.getAnalytics(),
  ]);
  catalogue = items;
  byId('evidence-items').textContent = String(items.length);
  byId('evidence-orders').textContent = String(orders.length);
  byId('evidence-conversions').textContent = String(analytics.conversion_count);
  renderInsights(orders, analytics);
  renderCatalogueTable();
}

function renderInsights(orders, analytics) {
  const recentOrders = orders.slice(-3).reverse();
  insights.innerHTML = `
    <div class="insight-block">
      <h3>Analytics</h3>
      <p>Revenue ${money(analytics.revenue_total)} · Visits ${analytics.site_visits}</p>
      <p>Viewed items: ${formatList(analytics.most_viewed_items)}</p>
      <p>Popular genres: ${formatList(analytics.most_popular_genres)}</p>
    </div>
    <div class="insight-block">
      <h3>Recent Orders</h3>
      ${recentOrders.length ? recentOrders.map(order => `
        <p><strong>${escapeHtml(order.order_id)}</strong> ${escapeHtml(order.customer.email)} · ${money(order.total)}</p>
      `).join('') : '<p>No persisted orders yet.</p>'}
    </div>`;
}

function renderCatalogueTable() {
  if (catalogue.length === 0) {
    table.innerHTML = 'No catalogue items saved.';
    return;
  }

  table.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Type</th>
          <th>Name</th>
          <th>Price</th>
          <th>Stock</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        ${catalogue.map(item => `
          <tr>
            <td>${item.isbn}</td>
            <td>${escapeHtml(item.item_type)}</td>
            <td>${escapeHtml(item.name)}</td>
            <td>${money(item.price)}</td>
            <td>${item.stock}</td>
            <td class="table-actions">
              <button class="secondary-action" type="button" data-edit-item="${item.isbn}">
                <i class="ti ti-pencil" aria-hidden="true"></i> Edit
              </button>
              <button class="danger-action" type="button" data-delete-item="${item.isbn}">
                <i class="ti ti-trash" aria-hidden="true"></i> Delete
              </button>
            </td>
          </tr>
        `).join('')}
      </tbody>
    </table>`;
}

async function loadItemIntoForm(itemId) {
  try {
    const item = await bookStoreApi.getCatalogueItem(itemId);
    form.elements.editing_id.value = item.isbn;
    form.elements.item_type.value = item.item_type;
    form.elements.item_type.disabled = true;
    form.elements.identifier.value = item.isbn;
    form.elements.identifier.readOnly = true;
    form.elements.price.value = item.price;
    form.elements.name.value = item.name;
    form.elements.author.value = item.author || '';
    form.elements.genre.value = item.category || item.genre || '';
    form.elements.edition.value = item.edition || '';
    form.elements.pages.value = item.pages || 0;
    form.elements.stock.value = item.stock || 0;
    formTitle.textContent = `Edit Item ${item.isbn}`;
    output.innerHTML = `<pre>${escapeHtml(JSON.stringify(item, null, 2))}</pre>`;
  } catch (error) {
    toast.show(error.message);
  }
}

async function deleteItem(itemId) {
  const data = new FormData(form);
  try {
    const result = await bookStoreApi.deleteCatalogueItem(itemId, {
      employee_id: data.get('employee_id'),
      access_code: data.get('access_code'),
    });
    toast.show(result.message);
    output.textContent = result.message;
    resetForm(false);
    await loadAdminData();
  } catch (error) {
    toast.show(error.message);
  }
}

function resetForm(withDefaults) {
  const employeeId = form.elements.employee_id.value || 'emp-1';
  const accessCode = form.elements.access_code.value;
  form.reset();
  form.elements.employee_id.value = employeeId;
  form.elements.access_code.value = accessCode;
  form.elements.editing_id.value = '';
  form.elements.item_type.disabled = false;
  form.elements.identifier.readOnly = false;
  formTitle.textContent = 'Add Catalogue Item';

  if (withDefaults) {
    form.elements.identifier.value = '88';
    form.elements.price.value = '18.50';
    form.elements.name.value = 'Design Patterns Pocket Guide';
    form.elements.author.value = 'A. Designer';
    form.elements.genre.value = 'Technology';
    form.elements.edition.value = 'First';
    form.elements.pages.value = '120';
    form.elements.stock.value = '5';
    output.textContent = 'Ready';
  }
}

function formatList(values) {
  return values && values.length ? values.map(value => escapeHtml(value)).join(', ') : 'None yet';
}

loadAdminData().catch(error => {
  table.textContent = 'Catalogue could not be loaded.';
  toast.show(error.message);
});
