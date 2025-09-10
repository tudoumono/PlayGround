/**
 * better-sqlite3 接続管理
 * - 初回起動時にDB/テーブルを自動作成
 * - 会社環境配布では%APPDATA%配下のDBを既定とする
 */
import { mkdirSync, existsSync } from 'node:fs';
import { dirname } from 'node:path';
import { getDefaultDbPath } from '@/env/paths';

type Stmt = { run: (...args: unknown[]) => unknown; get: (...args: unknown[]) => unknown; all: (...args: unknown[]) => unknown };
interface SqliteDB {
  pragma(sql: string): unknown;
  exec(sql: string): unknown;
  prepare(sql: string): Stmt;
}

let db: SqliteDB | null = null;

/** DB接続を取得（未接続なら初期化） */
export function getDb(customPath?: string): SqliteDB {
  if (process.env.SAFE_MODE === 'true') {
    throw new Error('DB disabled in SAFE_MODE');
  }
  if (db) return db;
  const dbPath = customPath ?? process.env.APP_DB_PATH ?? getDefaultDbPath();
  const dir = dirname(dbPath);
  if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
  // 動的読み込みでネイティブ拡張の読み込み失敗を回避（SAFE_MODEで未使用にできる）
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  const Better = require('better-sqlite3') as unknown as { new (path: string): SqliteDB };
  db = new Better(dbPath);
  db.pragma('journal_mode = WAL');
  bootstrapSchema(db);
  return db;
}

/** スキーマ初期化（必要なテーブルのみ作成） */
function bootstrapSchema(conn: SqliteDB): void {
  conn.exec(`
    CREATE TABLE IF NOT EXISTS settings (
      key TEXT PRIMARY KEY,
      value TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS personas (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      system_prompt TEXT NOT NULL,
      allowed_tools TEXT NOT NULL,
      default_model TEXT,
      temperature REAL
    );

    CREATE TABLE IF NOT EXISTS conversations (
      id TEXT PRIMARY KEY,
      title TEXT,
      persona_id TEXT,
      l3_store_id TEXT,
      last_response_id TEXT,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS messages (
      id TEXT PRIMARY KEY,
      conversation_id TEXT NOT NULL,
      role TEXT NOT NULL,
      content TEXT NOT NULL,
      response_id TEXT,
      tool_calls TEXT,
      created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS vector_stores_cache (
      id TEXT PRIMARY KEY,
      layer TEXT NOT NULL,
      name TEXT,
      files_count INTEGER,
      size_bytes INTEGER,
      synced_at TEXT
    );

    CREATE TABLE IF NOT EXISTS vector_store_files_cache (
      file_id TEXT PRIMARY KEY,
      store_id TEXT NOT NULL,
      filename TEXT NOT NULL,
      bytes INTEGER,
      status TEXT,
      synced_at TEXT,
      created_at TEXT
    );
  `);

  // 既存DBへのカラム追加（存在しない場合のみ）
  ensureColumn(conn, 'conversations', 'last_response_id', 'TEXT');
  ensureColumn(conn, 'messages', 'response_id', 'TEXT');
}

function ensureColumn(conn: SqliteDB, table: string, column: string, type: string) {
  const rows = conn.prepare(`PRAGMA table_info(${table})`).all() as { name: string }[];
  const found = rows.some((r) => r.name === column);
  if (!found) {
    conn.exec(`ALTER TABLE ${table} ADD COLUMN ${column} ${type}`);
  }
}
