export function loadingState(label) {
  return `
    <div class="loading-state">
      <i class="ti ti-loader-2" aria-hidden="true"></i>
      ${label}
    </div>`;
}

export function emptyState(icon, title, description, extra = '') {
  return `
    <div class="empty-state">
      <i class="ti ${icon}" aria-hidden="true"></i>
      <div class="empty-state-title">${title}</div>
      <p>${description}</p>
      ${extra}
    </div>`;
}
