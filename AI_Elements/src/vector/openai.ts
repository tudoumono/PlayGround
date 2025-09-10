/**
 * Vectorアダプタ（OpenAI実装の雛形）
 * NOTE: 実APIのエンドポイント/ペイロードはContext7で最新仕様を確認してから使用すること。
 */
import type { VectorAdapter } from '@/vector/adapter';
import type { VectorFileMeta, VectorLayer, VectorStoreMeta } from '@/vector/vectorStores';
import { httpJson } from '@/net/httpClient';

export function createOpenAIVectorAdapter(apiKey: string): VectorAdapter {
  const headers = { Authorization: `Bearer ${apiKey}`, 'Content-Type': 'application/json' };

  return {
    async listStores(): Promise<VectorStoreMeta[]> {
      // TODO: GET /v1/vector_stores
      const res = await httpJson<{ data?: { id: string; name?: string }[] }>({
        method: 'GET',
        url: 'https://api.openai.com/v1/vector_stores',
        headers,
      });
      if (res.status === 200 && res.data?.data) {
        return res.data.data.map((s) => ({ id: s.id, layer: 'L2', name: s.name ?? s.id }));
      }
      return [];
    },

    async listFiles(storeId: string): Promise<VectorFileMeta[]> {
      // TODO: GET /v1/vector_stores/{id}/files もしくは files.list でのフィルタ
      const res = await httpJson<{ data?: { id: string; filename?: string; bytes?: number; status?: string; created_at?: number }[] }>({
        method: 'GET',
        url: `https://api.openai.com/v1/vector_stores/${storeId}/files`,
        headers,
      });
      if (res.status === 200 && res.data?.data) {
        return res.data.data.map((f) => ({
          fileId: f.id,
          filename: f.filename ?? f.id,
          bytes: f.bytes ?? 0,
          status: (f.status as any) ?? 'ready',
          createdAt: f.created_at ? new Date(f.created_at * 1000).toISOString() : undefined,
        }));
      }
      return [];
    },

    async createStore(layer: VectorLayer, name: string): Promise<VectorStoreMeta> {
      // TODO: POST /v1/vector_stores
      const res = await httpJson<{ id?: string; name?: string }>({
        method: 'POST',
        url: 'https://api.openai.com/v1/vector_stores',
        headers,
        body: JSON.stringify({ name }),
      });
      if (res.status >= 200 && res.status < 300 && (res.data?.id || res.data?.name)) {
        return { id: (res.data?.id as string) ?? name, layer, name: res.data?.name ?? name };
      }
      throw new Error(`Failed to create vector store: ${res.status}`);
    },

    async deleteStore(storeId: string): Promise<void> {
      // TODO: DELETE /v1/vector_stores/{id}
      const res = await httpJson({
        method: 'DELETE',
        url: `https://api.openai.com/v1/vector_stores/${storeId}`,
        headers,
      });
      if (res.status >= 200 && res.status < 300) return;
      throw new Error(`Failed to delete store: ${res.status}`);
    },

    async addFile(storeId: string, filename: string, bytes: number): Promise<VectorFileMeta> {
      // TODO: POST /v1/vector_stores/{id}/files または files.upload 後にリンク
      // ここではメタのみ生成（実運用時はmultipartアップロードが必要）
      return { fileId: `${storeId}:${filename}`, filename, bytes, status: 'in_progress' };
    },

    async removeFile(storeId: string, fileId: string): Promise<void> {
      // TODO: DELETE /v1/vector_stores/{id}/files/{fileId}
      void storeId;
      void fileId;
    },

    async search(q: string): Promise<{ text: string; sourceId: string }[]> {
      // TODO: Responses APIのfile_search連携を使用
      void q;
      return [];
    },
  };
}

