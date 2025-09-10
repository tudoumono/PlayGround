/**
 * Chatタブ（暫定）
 * - Elements導入前の簡易UI
 */
"use client";
import { useState } from "react";
import { useChat } from "@ai-sdk/react";
import { TextStreamChatTransport } from "ai";
// 一時的にローカルラッパー版を使用（@ai-sdk/uiが公開され次第差し替え）
import { Chat, MessageList, Message, Composer } from "../components/elements";

export default function Page() {
  const { messages, sendMessage, isLoading } = useChat({
    transport: new TextStreamChatTransport({ api: '/api/chat' }),
  });

  const onSend = (text: string) => {
    void sendMessage({ text });
  };

  return (
    <Chat>
      <MessageList>
        {messages.map((m: any) => (
          <Message key={m.id} role={m.role}>
            {m.parts?.map((p: any, i: number) => p.type === 'text' ? <span key={i}>{p.text}</span> : null)}
          </Message>
        ))}
      </MessageList>
      <Composer onSend={onSend} />
    </Chat>
  );
}
