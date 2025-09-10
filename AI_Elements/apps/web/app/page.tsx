/**
 * Chatタブ（暫定）
 * - Elements導入前の簡易UI
 */
"use client";
import { useState } from "react";
import { Chat, MessageList, Message, Composer } from "../components/elements";

export default function Page() {
  const [messages, setMessages] = useState<{ role: "user"|"assistant"; content: string }[]>([]);

  const onSend = (text: string) => {
    setMessages((m) => [...m, { role: "user", content: text }, { role: "assistant", content: "" }]);
    const reply = `Echo: ${text}`;
    let i = 0;
    const timer = setInterval(() => {
      setMessages((m) => {
        const last = m[m.length - 1];
        if (!last || last.role !== "assistant") return m;
        return m.slice(0, -1).concat({ ...last, content: last.content + (reply[i] || "") });
      });
      i++;
      if (i >= reply.length) clearInterval(timer);
    }, 20);
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
