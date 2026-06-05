import { readFileSync } from 'node:fs';

export const sampleBooks = [
  { isbn: 2, name: 'Fahrenheit 451', author: 'Ray Bradbury', genre: 'Sci-Fi', pages: 256 },
  { isbn: 1, name: 'The Great Gatsby', author: 'F. Scott Fitzgerald', genre: 'Classic', pages: 180 },
];

export const cartWithPhysicalItems = {
  items: [
    { isbn: 1, name: 'The Great Gatsby', price: '21.99', quantity: 2 },
    { isbn: 2, name: 'Fahrenheit 451', price: '19.99', quantity: 1 },
  ],
  summary: {
    total_items: 3,
    subtotal: '63.97',
    shipping: '3.99',
    total: '67.96',
    requires_shipping: true,
  },
};

export const loggedInCustomer = {
  name: 'Saad',
  email: 'saad@example.com',
  shipping_address: {
    street: '1 Main St',
    city: 'Melbourne',
    state: 'VIC',
    postcode: '3000',
  },
};

export const physicalCartSummary = {
  total_items: 1,
  subtotal: '21.99',
  shipping: '3.99',
  total: '25.98',
  requires_shipping: true,
};

export function readProjectFile(relativePath) {
  return readFileSync(new URL(relativePath, import.meta.url), 'utf8');
}
