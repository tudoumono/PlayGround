// Root-level PostCSS config to support Next.js resolving in monorepo.
// Tailwind v4 uses '@tailwindcss/postcss' as the PostCSS plugin.
module.exports = {
  plugins: {
    '@tailwindcss/postcss': {},
    autoprefixer: {},
  },
};

