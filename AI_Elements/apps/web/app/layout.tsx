/**
 * アプリ共通レイアウト
 * - ヘッダー（タブ）/ コンテンツ領域
 * - 将来的にAI Elementsのレイアウトへ置換
 */
import './globals.css';
import Link from 'next/link';
import type { ReactNode } from 'react';

export const metadata = {
  title: 'AI Elements App',
  description: 'Next.js + AI Elements (skeleton)',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ja">
      <body>
        <header className="topbar">
          <div className="brand">AI Elements アプリ</div>
          <nav className="tabs">
            <Link href="/" className="tab">チャット</Link>
            <Link href="/settings" className="tab">設定</Link>
            <Link href="/vector" className="tab">ベクター</Link>
            <Link href="/personas" className="tab">ペルソナ</Link>
            <Link href="/logs" className="tab">ログ</Link>
          </nav>
        </header>
        <main className="container">{children}</main>
        <footer className="footer">プレビューUI（配線作業進行中）</footer>
      </body>
    </html>
  );
}
