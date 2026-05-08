/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        'control-panel-grey': '#e5e7eb',
        'display-black': '#11161c',
        'obsidian-grey': '#000000',
        'digital-white': '#ffffff',
        graphite: '#bbbbbb',
        'steel-grey': '#a3a3a3',
        'slate-blue': '#575c75',
        'urgency-red': '#f43325',
        'active-blue': '#0078a8',
      },
      borderRadius: {
        cards: '127.397px',
        pills: '9999px',
        buttons: '270.89px',
      },
      fontFamily: {
        'proxima-nova': ['var(--font-proxima-nova)'],
        'sf-mono': ['var(--font-sf-mono)'],
        'helvetica-neue': ['var(--font-helvetica-neue)'],
        doto: ['var(--font-doto)'],
      },
      boxShadow: {
        subtle: 'rgba(0, 0, 0, 0.8) 0px 0px 2px 0px',
        'subtle-2': 'rgba(255, 255, 255, 0.5) 0px 0px 2px 0px',
      },
    },
  },
  plugins: [],
};
