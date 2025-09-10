/**
 * 会話/メッセージの永続化（SQLite）
 */
import { getDb } from '@/db/connection';
import { randomUUID } from 'node:crypto';

export interface Conversation {
  id: string;
  title: string | null;
  personaId: string | null;
  l3StoreId: string | null;
  lastResponseId: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface Message {
  id: string;
  conversationId: string;
  role: 'user' | 'assistant' | 'tool' | 'system';
  content: string;
  responseId?: string | null;
  toolCalls?: unknown;
  createdAt: string;
}

export function createConversation(title: string | null, personaId: string | null, l3StoreId: string | null): Conversation {
  if (process.env.SAFE_MODE === 'true') {
    const id = randomUUID();
    const now = new Date().toISOString();
    const conv: Conversation = { id, title, personaId, l3StoreId, lastResponseId: null, createdAt: now, updatedAt: now };
    mem.conversations.unshift(conv);
    return conv;
  }
  const db = getDb();
  const id = randomUUID();
  const now = new Date().toISOString();
  db.prepare('INSERT INTO conversations(id, title, persona_id, l3_store_id, last_response_id, created_at, updated_at) VALUES(?,?,?,?,?,?,?)')
    .run(id, title, personaId, l3StoreId, null, now, now);
  return { id, title, personaId, l3StoreId, lastResponseId: null, createdAt: now, updatedAt: now };
}

export function setConversationLastResponseId(conversationId: string, responseId: string): void {
  if (process.env.SAFE_MODE === 'true') {
    const c = mem.conversations.find((x) => x.id === conversationId);
    if (c) c.lastResponseId = responseId;
    return;
  }
  const db = getDb();
  const now = new Date().toISOString();
  db.prepare('UPDATE conversations SET last_response_id = ?, updated_at = ? WHERE id = ?')
    .run(responseId, now, conversationId);
}

export function appendMessage(msg: Omit<Message, 'id' | 'createdAt'>): Message {
  if (process.env.SAFE_MODE === 'true') {
    const id = randomUUID();
    const now = new Date().toISOString();
    const m: Message = { ...msg, id, createdAt: now };
    mem.messages.push(m);
    return m;
  }
  const db = getDb();
  const id = randomUUID();
  const now = new Date().toISOString();
  db.prepare('INSERT INTO messages(id, conversation_id, role, content, response_id, tool_calls, created_at) VALUES(?,?,?,?,?,?,?)')
    .run(id, msg.conversationId, msg.role, msg.content, msg.responseId ?? null, msg.toolCalls ? JSON.stringify(msg.toolCalls) : null, now);
  db.prepare('UPDATE conversations SET updated_at = ? WHERE id = ?').run(now, msg.conversationId);
  return { ...msg, id, createdAt: now };
}

export function listConversations(limit = 100): Conversation[] {
  if (process.env.SAFE_MODE === 'true') return mem.conversations.slice(0, limit);
  const db = getDb();
  const rows = db.prepare('SELECT id, title, persona_id as personaId, l3_store_id as l3StoreId, last_response_id as lastResponseId, created_at as createdAt, updated_at as updatedAt FROM conversations ORDER BY updated_at DESC LIMIT ?').all(limit) as Conversation[];
  return rows;
}

export function getConversation(id: string): Conversation | null {
  if (process.env.SAFE_MODE === 'true') return mem.conversations.find((x) => x.id === id) ?? null;
  const db = getDb();
  const row = db.prepare('SELECT id, title, persona_id as personaId, l3_store_id as l3StoreId, last_response_id as lastResponseId, created_at as createdAt, updated_at as updatedAt FROM conversations WHERE id = ?').get(id) as Conversation | undefined;
  return row ?? null;
}

// SAFE_MODE用のメモリ格納
const mem: { conversations: Conversation[]; messages: Message[] } = { conversations: [], messages: [] };
