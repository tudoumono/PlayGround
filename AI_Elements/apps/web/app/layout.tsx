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
          <div className="brand">AI Elements App</div>
          <nav className="tabs">
            <Link href="/" className="tab">Chat</Link>
            <Link href="/settings" className="tab">Settings</Link>
            <Link href="/vector" className="tab">Vector</Link>
            <Link href="/personas" className="tab">Personas</Link>
            <Link href="/logs" className="tab">Logs</Link>
          </nav>
        </header>
        <main className="container">{children}</main>
        <footer className="footer">Preview UI — backend wiring WIP</footer>
      </body>
    </html>
  );
}

