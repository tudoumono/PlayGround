import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        bg: '#0b0f14',
        panel: '#121822',
        accent: '#2ea3ff',
        muted: '#8aa0b8',
        border: '#223048',
      },
    },
  },
  plugins: [],
};

export default config;

