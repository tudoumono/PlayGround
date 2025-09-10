/**
 * Chatタブ（暫定）
 * - Elements導入前の簡易UI
 */
"use client";
import { useState } from "react";
// 一時的にローカルラッパー版を使用（@ai-sdk/uiが公開され次第差し替え）
import { Chat, MessageList, Message, Composer } from "../components/elements";

export default function Page() {
  const [messages, setMessages] = useState<{ role: "user"|"assistant"; content: string }[]>([]);

  const onSend = (text: string) => {
    setMessages((m) => [...m, { role: "user", content: text }, { role: "assistant", content: "" }]);
    // /api/chat にPOSTし、toTextStreamResponse()の生テキストを逐次描画
    void (async () => {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: text }),
      });
      if (!res.body) return;
      const reader = res.body.getReader();
      const decoder = new TextDecoder('utf-8');
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        setMessages((m) => {
          const last = m[m.length - 1];
          if (!last || last.role !== 'assistant') return m;
          return m.slice(0, -1).concat({ ...last, content: last.content + chunk });
        });
      }
    })();
  };

  return (
    <Chat>
      <MessageList>
        {messages.map((m, idx) => (
          <Message key={idx} role={m.role}>{m.content}</Message>
        ))}
      </MessageList>
      <Composer onSend={onSend} />
    </Chat>
  );
}
