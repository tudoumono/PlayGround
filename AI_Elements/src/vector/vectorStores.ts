/**
 * Vector Store（L1/L2/L3）管理
 * - L1: 事前定義（読取専用）
 * - L2: ユーザー管理（CRUD可）
 * - L3: 会話限定（終了時クリア可）
 * 既定の検索順: L3 → L2 → L1（重み付けは設定で調整）
 */

export type VectorLayer = 'L1' | 'L2' | 'L3';

export interface VectorStoreMeta {
  id: string;
  layer: VectorLayer;
  name: string;
  filesCount?: number;
  sizeBytes?: number;
  updatedAt?: string;
}

export interface VectorFileMeta {
  fileId: string;
  filename: string;
  bytes: number;
  status: 'in_progress' | 'ready' | 'error';
  createdAt?: string;
}

import type { VectorAdapter } from '@/vector/adapter';
import { getDb } from '@/db/connection';

let adapter: VectorAdapter | null = null;

/** 使用するVectorアダプタを差し替える（mock / openai 等） */
export function setVectorAdapter(a: VectorAdapter): void {
  adapter = a;
}

/** ストア一覧（キャッシュ優先→アダプタで同期）。 */
export async function listStores(): Promise<VectorStoreMeta[]> {
  if (process.env.SAFE_MODE === 'true') return [];
  const db = getDb();
  const cached = db.prepare('SELECT id, layer, name, files_count AS filesCount, size_bytes AS sizeBytes, synced_at AS updatedAt FROM vector_stores_cache').all() as VectorStoreMeta[];
  if (!adapter) return cached;
  try {
    const latest = await adapter.listStores();
    // キャッシュ更新（単純上書き）
    const up = db.prepare('INSERT OR REPLACE INTO vector_stores_cache(id, layer, name, files_count, size_bytes, synced_at) VALUES(?,?,?,?,?,?)');
    for (const s of latest) {
      up.run(s.id, s.layer, s.name, s.filesCount ?? null, s.sizeBytes ?? null, new Date().toISOString());
    }
    return latest;
  } catch {
    return cached;
  }
}

/** 指定ストアのファイル一覧。filename/bytes/statusをUIに表示。 */
export async function listFilesInStore(storeId: string): Promise<VectorFileMeta[]> {
  if (process.env.SAFE_MODE === 'true') return [];
  const db = getDb();
  const cached = db.prepare('SELECT file_id AS fileId, store_id, filename, bytes, status, created_at AS createdAt FROM vector_store_files_cache WHERE store_id = ? ORDER BY created_at DESC').all(storeId) as VectorFileMeta[];
  if (!adapter) return cached;
  try {
    const latest = await adapter.listFiles(storeId);
    const up = db.prepare('INSERT OR REPLACE INTO vector_store_files_cache(file_id, store_id, filename, bytes, status, synced_at, created_at) VALUES(?,?,?,?,?,?,COALESCE(?, created_at))');
    for (const f of latest) {
      up.run(f.fileId, storeId, f.filename, f.bytes, f.status, new Date().toISOString(), f.createdAt ?? null);
    }
    return latest;
  } catch {
    return cached;
  }
}

/** ストア作成（L2/L3向け）。 */
export async function createStore(layer: VectorLayer, name: string): Promise<VectorStoreMeta> {
  if (!adapter) throw new Error('Vector adapter not set');
  const store = await adapter.createStore(layer, name);
  if (process.env.SAFE_MODE !== 'true') {
    const db = getDb();
    db.prepare('INSERT OR REPLACE INTO vector_stores_cache(id, layer, name, files_count, size_bytes, synced_at) VALUES(?,?,?,?,?,?)')
      .run(store.id, store.layer, store.name, store.filesCount ?? 0, store.sizeBytes ?? 0, new Date().toISOString());
  }
  return store;
}

/** ストア削除（L2/L3向け）。 */
export async function deleteStore(storeId: string): Promise<void> {
  if (!adapter) throw new Error('Vector adapter not set');
  await adapter.deleteStore(storeId);
  if (process.env.SAFE_MODE !== 'true') {
    const db = getDb();
    db.prepare('DELETE FROM vector_stores_cache WHERE id = ?').run(storeId);
    db.prepare('DELETE FROM vector_store_files_cache WHERE store_id = ?').run(storeId);
  }
}

/** ファイル追加（アップロード→インデックス）。 */
export async function addFileToStore(storeId: string, filename: string, bytes: number): Promise<VectorFileMeta> {
  if (!adapter) throw new Error('Vector adapter not set');
  const meta = await adapter.addFile(storeId, filename, bytes);
  if (process.env.SAFE_MODE !== 'true') {
    const db = getDb();
    db.prepare('INSERT OR REPLACE INTO vector_store_files_cache(file_id, store_id, filename, bytes, status, synced_at, created_at) VALUES(?,?,?,?,?,?,?)')
      .run(meta.fileId, storeId, meta.filename, meta.bytes, meta.status, new Date().toISOString(), meta.createdAt ?? new Date().toISOString());
  }
  return meta;
}

/** ファイル削除。 */
export async function removeFileFromStore(storeId: string, fileId: string): Promise<void> {
  if (!adapter) throw new Error('Vector adapter not set');
  await adapter.removeFile(storeId, fileId);
  if (process.env.SAFE_MODE !== 'true') {
    const db = getDb();
    db.prepare('DELETE FROM vector_store_files_cache WHERE file_id = ?').run(fileId);
  }
}

/**
 * 層を跨いだ検索の合成（スコア/新鮮度で統合）。
 * - 既定は L3→L2→L1 優先。設定で重み付け変更可。
 * NOTE: 実装はOpenAIのFile Searchを活用。ここではアダプタを委譲。
 */
export async function searchAcrossLayers(q: string): Promise<{ text: string; sourceId: string }[]> {
  if (!adapter) return [];
  return adapter.search(q);
}
