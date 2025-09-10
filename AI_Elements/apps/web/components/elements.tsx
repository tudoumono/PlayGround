/**
 * Elements互換の軽量ラッパー（暫定）
 * - 目的: @ai-sdk/ui を導入するまでの置き換えポイント。
 * - 方針: API最小限（Chat / MessageList / Message / Composer）。
 * - 導入後: 下記のTODOの通り、@ai-sdk/ui からの再エクスポートに差し替える。
 */
import type { ReactNode } from 'react';

export function Chat({ children }: { children: ReactNode }) {
  return <section className="panel">{children}</section>;
}

export function MessageList({ children }: { children: ReactNode }) {
  return <div className="messages">{children}</div>;
}

export function Message({ role, children }: { role: 'user'|'assistant'|'tool'|'system'; children: ReactNode }) {
  return <div className={`message ${role}`}>{children}</div>;
}

export function Composer({ onSend, disabled }: { onSend: (text: string) => void; disabled?: boolean }) {
  return (
    <div className="composer">
      <select className="min-w-28">
        <option>gpt-5</option>
        <option>gpt-4o</option>
        <option>gpt-4o-mini</option>
      </select>
      <input
        className="flex-1"
        placeholder="メッセージを入力"
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            const v = (e.target as HTMLInputElement).value.trim();
            if (v) { onSend(v); (e.target as HTMLInputElement).value = ''; }
          }
        }}
        disabled={disabled}
      />
      <button
        onClick={() => {
          const input = (document.activeElement as HTMLInputElement) || document.querySelector('input[placeholder="メッセージを入力"]') as HTMLInputElement | null;
          const v = input?.value?.trim();
          if (v) { onSend(v); if (input) input.value = ''; }
        }}
        disabled={disabled}
      >Send</button>
    </div>
  );
}

// TODO(you, 2025-09-10): @ai-sdk/ui導入後に以下のように差し替え
// export { Chat, MessageList, Message, Composer } from '@ai-sdk/ui';

