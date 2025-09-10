/**
 * ログ機構（Next.js側の簡易実装）
 * - 目的: API/UIで参照可能なアプリ内ログを提供（ファイル書き込みはしない）
 * - 実装: プロセス内リングバッファ（最大1000件）。APIから取得/追加/クリア。
 */

export type LogLevel = 'info' | 'warn' | 'error' | 'debug';

export interface LogEntry {
  ts: string; // ISO8601
  level: LogLevel;
  tag: string;
  message: string;
}

const MAX = 1000;
const buffer: LogEntry[] = [];

/** ログを追加する */
export function appendLog(level: LogLevel, tag: string, message: string): void {
  const entry: LogEntry = { ts: new Date().toISOString(), level, tag, message };
  buffer.push(entry);
  if (buffer.length > MAX) buffer.splice(0, buffer.length - MAX);
}

/** 直近n件（デフォルト200件）を新しい順で返す */
export function getLogs(limit = 200): LogEntry[] {
  return buffer.slice(Math.max(0, buffer.length - limit)).reverse();
}

/** バッファをクリアする */
export function clearLogs(): void {
  buffer.length = 0;
}

