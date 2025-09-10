/**
 * Chatタブ（暫定）
 * - Elements導入前の簡易UI
 */
"use client";
import { useRef, useState } from "react";

export default function Page() {
  const [messages, setMessages] = useState<{ role: "user"|"assistant"; content: string }[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  function send() {
    const text = (inputRef.current?.value || "").trim();
    if (!text) return;
    inputRef.current!.value = "";
    setMessages((m) => [...m, { role: "user", content: text }, { role: "assistant", content: "" }]);
    // 擬似ストリーム
    const reply = `Echo: ${text}`;
    let i = 0;
    const timer = setInterval(() => {
      setMessages((m) => {
        const last = m[m.length - 1];
        if (!last || last.role !== "assistant") return m;
        const updated = m.slice(0, -1).concat({ ...last, content: last.content + (reply[i] || "") });
        return updated;
      });
      i++;
      if (i >= reply.length) clearInterval(timer);
    }, 20);
  }

  return (
    <section className="panel">
      <div className="messages">
        {messages.map((m, idx) => (
          <div key={idx} className={`message ${m.role}`}>{m.content}</div>
        ))}
      </div>
      <div className="composer">
        <select>
          <option>gpt-5</option>
          <option>gpt-4o</option>
          <option>gpt-4o-mini</option>
        </select>
        <input ref={inputRef} placeholder="メッセージを入力" onKeyDown={(e) => e.key === 'Enter' && send()} />
        <button onClick={send}>Send</button>
      </div>
    </section>
  );
}

