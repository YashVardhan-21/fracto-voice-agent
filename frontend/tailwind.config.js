/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'fracto-blue': '#2563eb',
        'fracto-blue-light': '#3b82f6',
        'fracto-blue-dark': '#1d4ed8',
        'fracto-gray': '#6b7280',
        'fracto-gray-light': '#9ca3af',
        'fracto-gray-dark': '#374151',
      },
      fontFamily: {
        'sans': ['Inter', 'ui-sans-serif', 'system-ui'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}