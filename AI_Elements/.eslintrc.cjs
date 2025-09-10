/**
 * ESLint 設定（AI_Elements/ TypeScript用）
 * - 目的: JSDoc必須、`any`禁止、基本Lintの適用
 */
module.exports = {
  root: true,
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint', 'jsdoc'],
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:jsdoc/recommended',
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
  },
  rules: {
    '@typescript-eslint/no-explicit-any': 'error',
    'jsdoc/require-jsdoc': [
      'error',
      {
        contexts: [
          'TSInterfaceDeclaration',
          'TSTypeAliasDeclaration',
          'FunctionDeclaration',
          'MethodDefinition',
          'ArrowFunctionExpression',
          'ClassDeclaration',
        ],
        publicOnly: true,
        require: {
          ClassDeclaration: true,
          MethodDefinition: true,
          FunctionDeclaration: true,
          ArrowFunctionExpression: false,
        },
      },
    ],
    'jsdoc/require-returns-description': 'warn',
    'jsdoc/require-param-description': 'warn',
  },
  settings: {
    jsdoc: {
      mode: 'typescript',
    },
  },
};

