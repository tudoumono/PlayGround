/**
 * Vectorアダプタ（モック実装）
 * - SQLiteキャッシュをそのまま返す簡易実装
 * - OpenAI実装が整うまでのプレースホルダ
 */
import { getDb } from '@/db/connection';
import type { VectorAdapter } from '@/vector/adapter';
import type { VectorFileMeta, VectorLayer, VectorStoreMeta } from '@/vector/vectorStores';
import { randomUUID } from 'node:crypto';

export function createMockVectorAdapter(): VectorAdapter {
  return {
    async listStores(): Promise<VectorStoreMeta[]> {
      const db = getDb();
      return db
        .prepare(
          'SELECT id, layer, name, files_count AS filesCount, size_bytes AS sizeBytes, synced_at AS updatedAt FROM vector_stores_cache',
        )
        .all() as VectorStoreMeta[];
    },

    async listFiles(storeId: string): Promise<VectorFileMeta[]> {
      const db = getDb();
      return db
        .prepare(
          'SELECT file_id AS fileId, filename, bytes, status, created_at AS createdAt FROM vector_store_files_cache WHERE store_id = ? ORDER BY created_at DESC',
        )
        .all(storeId) as VectorFileMeta[];
    },

    async createStore(layer: VectorLayer, name: string): Promise<VectorStoreMeta> {
      const db = getDb();
      const id = randomUUID();
      const now = new Date().toISOString();
      db.prepare('INSERT OR REPLACE INTO vector_stores_cache(id, layer, name, files_count, size_bytes, synced_at) VALUES(?,?,?,?,?,?)')
        .run(id, layer, name, 0, 0, now);
      return { id, layer, name, filesCount: 0, sizeBytes: 0, updatedAt: now };
    },

    async deleteStore(storeId: string): Promise<void> {
      const db = getDb();
      db.prepare('DELETE FROM vector_stores_cache WHERE id = ?').run(storeId);
      db.prepare('DELETE FROM vector_store_files_cache WHERE store_id = ?').run(storeId);
    },

    async addFile(storeId: string, filename: string, bytes: number): Promise<VectorFileMeta> {
      const db = getDb();
      const fileId = randomUUID();
      const now = new Date().toISOString();
      db.prepare('INSERT OR REPLACE INTO vector_store_files_cache(file_id, store_id, filename, bytes, status, synced_at, created_at) VALUES(?,?,?,?,?,?,?)')
        .run(fileId, storeId, filename, bytes, 'ready', now, now);
      return { fileId, filename, bytes, status: 'ready', createdAt: now };
    },

    async removeFile(_storeId: string, fileId: string): Promise<void> {
      const db = getDb();
      db.prepare('DELETE FROM vector_store_files_cache WHERE file_id = ?').run(fileId);
    },

    async search(q: string): Promise<{ text: string; sourceId: string }[]> {
      // モック: 単純にヒットなし
      void q;
      return [];
    },
  };
}

