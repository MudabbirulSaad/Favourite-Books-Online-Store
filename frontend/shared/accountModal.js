import { bookStoreApi } from '../adapters/http/bookStoreApi.js';
import { clearCustomer, getStoredCustomer, storeCustomer } from './accountSession.js';
import { byId, escapeHtml } from './dom.js';

let activeAccountTab = 'login';

export function initAccountModal({ toast, onAccountChange } = {}) {
  const panel = byId('accountPanel');
  const toggle = byId('accountToggle');

  function currentCustomer() {
    return getStoredCustomer();
  }

  function renderAccountNav() {
    if (!toggle) return;

    const customer = currentCustomer();
    if (!customer) {
      toggle.classList.add('guest');
      toggle.setAttribute('aria-label', 'Login or register');
      toggle.innerHTML = `
        <i class="ti ti-user-plus" aria-hidden="true"></i>
        <span>Login / Register</span>`;
      return;
    }

    toggle.classList.remove('guest');
    toggle.setAttribute('aria-label', `Account for ${customer.name}`);
    toggle.innerHTML = `
      <i class="ti ti-user-circle" aria-hidden="true"></i>
      <span>${escapeHtml(customer.name)}</span>`;
  }

  function renderAccount() {
    renderAccountNav();
    if (!panel) return;

    const customer = currentCustomer();
    const status = byId('accountStatus');
    const forms = byId('accountForms');
    const tabs = byId('accountTabs');

    if (!customer) {
      status.innerHTML = `
        <div>
          <strong>Login or create an account before checkout.</strong>
          <span>Your saved delivery details will be used for future orders.</span>
        </div>`;
      tabs.hidden = false;
      forms.hidden = false;
      setAccountTab(activeAccountTab);
      return;
    }

    tabs.hidden = true;
    forms.hidden = true;
    status.innerHTML = `
      <div class="account-signed-in">
        <span class="account-avatar" aria-hidden="true">${escapeHtml(customer.name).slice(0, 1)}</span>
        <div>
          <strong>${escapeHtml(customer.name)}</strong>
          <span>${escapeHtml(customer.email)}</span>
        </div>
      </div>
      <button class="secondary-action" type="button" id="logoutButton">
        <i class="ti ti-logout" aria-hidden="true"></i> Logout
      </button>`;
    byId('logoutButton').addEventListener('click', () => {
      void handleLogout();
    });
  }

  function setAccountTab(tabName) {
    activeAccountTab = tabName;
    ['login', 'register'].forEach(name => {
      const selected = name === tabName;
      const tab = byId(`${name}Tab`);
      const form = byId(`${name}Form`);
      if (!tab || !form) return;
      tab.classList.toggle('active', selected);
      tab.setAttribute('aria-selected', selected ? 'true' : 'false');
      form.hidden = !selected;
      form.classList.toggle('active', selected);
    });
  }

  function openAccountModal(tabName = activeAccountTab) {
    if (!panel) {
      window.location.href = `index.html#accountPanel`;
      return;
    }

    panel.hidden = false;
    document.body.classList.add('modal-open');
    renderAccount();
    if (!currentCustomer()) {
      setAccountTab(tabName);
      const firstInput = byId(`${tabName}Form`)?.querySelector('input');
      if (firstInput) firstInput.focus();
    } else {
      byId('logoutButton')?.focus();
    }
  }

  function closeAccountModal() {
    if (!panel) return;
    panel.hidden = true;
    document.body.classList.remove('modal-open');
    if (window.location.hash === '#accountPanel') {
      history.replaceState(null, '', window.location.pathname + window.location.search);
    }
  }

  async function refreshAccountFromSession() {
    try {
      const customer = await bookStoreApi.getSessionCustomer();
      if (customer) {
        storeCustomer(customer);
      } else {
        clearCustomer();
      }
      renderAccount();
      if (onAccountChange) onAccountChange(customer);
      return customer;
    } catch {
      renderAccount();
      return currentCustomer();
    }
  }

  async function handleLogout() {
    try {
      await bookStoreApi.logoutCustomer();
    } catch (error) {
      toast?.show(error.message);
    }
    clearCustomer();
    renderAccount();
    if (onAccountChange) onAccountChange(null);
    toast?.show('Logged out');
  }

  async function handleLogin(event) {
    event.preventDefault();
    const data = new FormData(event.target);
    try {
      const customer = await bookStoreApi.loginCustomer(data.get('email'), data.get('password'));
      storeCustomer(customer);
      event.target.reset();
      renderAccount();
      closeAccountModal();
      if (onAccountChange) onAccountChange(customer);
      toast?.show(`Welcome back, ${customer.name}`);
    } catch (error) {
      toast?.show(error.message);
    }
  }

  async function handleRegister(event) {
    event.preventDefault();
    const data = new FormData(event.target);
    const payload = {
      name: data.get('name'),
      email: data.get('email'),
      password: data.get('password'),
      shipping_address: {
        street: data.get('street'),
        city: data.get('city'),
        state: data.get('state'),
        postcode: data.get('postcode'),
      },
    };

    try {
      const customer = await bookStoreApi.registerCustomer(payload);
      storeCustomer(customer);
      event.target.reset();
      renderAccount();
      closeAccountModal();
      if (onAccountChange) onAccountChange(customer);
      toast?.show(`Account created for ${customer.name}`);
    } catch (error) {
      toast?.show(error.message);
    }
  }

  function bindEvents() {
    toggle?.addEventListener('click', () => {
      openAccountModal();
    });

    if (!panel) return;

    panel.addEventListener('click', event => {
      if (event.target.id === 'accountPanel' || event.target.closest('[data-account-close]')) {
        closeAccountModal();
      }
    });

    byId('accountTabs')?.addEventListener('click', event => {
      const tab = event.target.closest('[data-account-tab]');
      if (!tab) return;
      setAccountTab(tab.dataset.accountTab);
    });

    byId('loginForm')?.addEventListener('submit', handleLogin);
    byId('registerForm')?.addEventListener('submit', handleRegister);

    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && !panel.hidden) {
        closeAccountModal();
      }
    });
  }

  bindEvents();
  renderAccountNav();

  return {
    close: closeAccountModal,
    open: openAccountModal,
    refresh: refreshAccountFromSession,
    render: renderAccount,
  };
}
