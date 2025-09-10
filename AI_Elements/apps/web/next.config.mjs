/**
 * Next.js 設定（App Router）
 * - 将来のElements導入/モノレポ対応のため最低限のみ。
 */
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    typedRoutes: true,
  },
};

export default nextConfig;

