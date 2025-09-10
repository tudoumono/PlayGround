/**
 * ログ機構（Next.js側の簡易実装）
 * - 目的: API/UIで参照可能なアプリ内ログを提供
 * - 実装: プロセス内リングバッファ（最大1000件）＋ファイル永続化（1行JSON）
 */
import { appendFileSync, mkdirSync, statSync, rmSync, existsSync } from 'node:fs';
import { dirname, resolve } from 'node:path';

export type LogLevel = 'info' | 'warn' | 'error' | 'debug';

export interface LogEntry {
  ts: string; // ISO8601
  level: LogLevel;
  tag: string;
  message: string;
}

const MAX = 1000;
const buffer: LogEntry[] = [];
const DEFAULT_LOG_PATH = resolve(process.cwd(), 'data', 'logs', 'app.log');
let logFilePath = DEFAULT_LOG_PATH;

/** ログを追加する */
export function appendLog(level: LogLevel, tag: string, message: string): void {
  const entry: LogEntry = { ts: new Date().toISOString(), level, tag, message };
  buffer.push(entry);
  if (buffer.length > MAX) buffer.splice(0, buffer.length - MAX);
  // ファイルへ追記（ディレクトリが無ければ作成）。失敗しても処理は継続。
  try {
    mkdirSync(dirname(logFilePath), { recursive: true });
    appendFileSync(logFilePath, JSON.stringify(entry) + '\n', { encoding: 'utf-8' });
  } catch {}
}

/** 直近n件（デフォルト200件）を新しい順で返す */
export function getLogs(limit = 200): LogEntry[] {
  return buffer.slice(Math.max(0, buffer.length - limit)).reverse();
}

/** バッファをクリアする */
export function clearLogs(): void {
  buffer.length = 0;
}

/** ログファイルのパスを取得（UI表示用） */
export function getLogFilePath(): string { return logFilePath; }

/** ログファイルのメタ情報 */
export function getLogFileInfo(): { path: string; exists: boolean; size: number } {
  try {
    const st = statSync(logFilePath);
    return { path: logFilePath, exists: true, size: st.size };
  } catch {
    return { path: logFilePath, exists: existsSync(dirname(logFilePath)), size: 0 };
  }
}

/** ログファイルを削除（存在しなければ何もしない） */
export function deleteLogFile(): void {
  try { rmSync(logFilePath, { force: true }); } catch {}
}

/** ログファイルの出力先を変更（必要時） */
export function setLogFilePath(p: string): void {
  if (!p) return;
  const abs = resolve(p);
  mkdirSync(dirname(abs), { recursive: true });
  logFilePath = abs;
}
