import { byId } from '../shared/dom.js';

export function createToast(id = 'toast') {
  const element = byId(id);
  let timeoutId;

  return {
    show(message, duration = 2400) {
      element.textContent = message;
      element.classList.add('show');
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => element.classList.remove('show'), duration);
    },
  };
}
