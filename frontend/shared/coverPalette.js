export const COVERS = [
  { bg: '#2C3E50', accent: '#E8C547' },
  { bg: '#8B2635', accent: '#F4C89B' },
  { bg: '#1B5E7B', accent: '#A8D8A8' },
  { bg: '#4A3728', accent: '#E8D5B0' },
  { bg: '#2D5A27', accent: '#F7E8A4' },
  { bg: '#5C3566', accent: '#FADCB5' },
];

export function coverFor(item) {
  return COVERS[item.cover % COVERS.length];
}
