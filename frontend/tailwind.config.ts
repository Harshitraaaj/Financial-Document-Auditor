import type { Config } from 'tailwindcss';

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          50: '#f7f8fa',
          100: '#eceff3',
          200: '#d6dce4',
          500: '#637083',
          700: '#344054',
          900: '#111827',
        },
        audit: {
          green: '#0f766e',
          amber: '#b45309',
          red: '#b42318',
          blue: '#2563eb',
        },
      },
      boxShadow: {
        panel: '0 1px 2px rgba(16, 24, 40, 0.06), 0 1px 3px rgba(16, 24, 40, 0.1)',
      },
    },
  },
  plugins: [],
} satisfies Config;

