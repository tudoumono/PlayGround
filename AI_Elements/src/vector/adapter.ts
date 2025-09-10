/**
 * VectorアダプタIF（mock / openai 実装を差し替え）
 */
import type { VectorFileMeta, VectorLayer, VectorStoreMeta } from '@/vector/vectorStores';

export interface VectorAdapter {
  listStores(): Promise<VectorStoreMeta[]>;
  listFiles(storeId: string): Promise<VectorFileMeta[]>;
  createStore(layer: VectorLayer, name: string): Promise<VectorStoreMeta>;
  deleteStore(storeId: string): Promise<void>;
  addFile(storeId: string, filename: string, bytes: number): Promise<VectorFileMeta>;
  removeFile(storeId: string, fileId: string): Promise<void>;
  search(q: string): Promise<{ text: string; sourceId: string }[]>;
}

