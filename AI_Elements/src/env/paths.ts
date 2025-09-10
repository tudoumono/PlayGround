/**
 * アプリのデータディレクトリ/DBパスを解決するヘルパー
 * - Windows: %APPDATA%/YourApp
 * - macOS: ~/Library/Application Support/YourApp
 * - Linux: ~/.config/YourApp
 */
import { join } from 'node:path';
import { homedir } from 'node:os';

const APP_NAME = process.env.APP_NAME ?? 'YourApp';

/** ユーザーデータディレクトリを返す（存在チェック/作成は呼び出し側で） */
export function getUserDataDir(): string {
  const platform = process.platform;
  if (platform === 'win32') {
    return join(process.env.APPDATA || join(homedir(), 'AppData', 'Roaming'), APP_NAME);
  }
  if (platform === 'darwin') {
    return join(homedir(), 'Library', 'Application Support', APP_NAME);
  }
  return join(homedir(), '.config', APP_NAME);
}

/** 既定のDBファイルパス */
export function getDefaultDbPath(): string {
  return join(getUserDataDir(), 'app.db');
}

