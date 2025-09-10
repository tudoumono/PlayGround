/**
 * Electron メインプロセス（雛形）
 * - 起動時にbootstrap()で設定/プロキシ/egress guardを適用
 * - テレメトリ/自動更新は使用しない（会社プロファイル準拠）
 */
// NOTE: ローカルフォルダ名とパッケージ名の衝突回避のため、フォルダを `app-electron/` に配置
// importを使うと tsc-alias が誤って相対に書き換える場合があるため、ここは require を使用
// eslint-disable-next-line @typescript-eslint/no-var-requires
const { app, BrowserWindow, session } = require('electron');
import type { OnBeforeRequestListenerDetails, CallbackResponse } from 'electron';
import path from 'node:path';
import { bootstrap } from '@/server/bootstrap';

process.env.ELECTRON_DISABLE_SECURITY_WARNINGS = 'true';
process.env.NEXT_TELEMETRY_DISABLED = '1';

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
    },
  });

  // NOTE: Next.jsのURLがあればそれを、なければビルド済み静的UIをロード
  const startUrl = process.env.APP_START_URL;
  if (startUrl) {
    win.loadURL(startUrl);
  } else {
    const uiFile = path.resolve(__dirname, '../dist/ui/index.html');
    win.loadFile(uiFile).catch(() => win.loadURL('about:blank'));
  }
}

app.whenReady().then(async () => {
  // 設定の適用
  bootstrap();

  // 会社プロファイル時に外部CSPや外部送信をさらに制限したい場合はここで`session`にルールを設定
  session.defaultSession.webRequest.onBeforeRequest(
    (
      _details: OnBeforeRequestListenerDetails,
      callback: (response: CallbackResponse) => void,
    ) => {
      // 例: ここでホワイトリスト制御などを行う。現状は全て許可。
      callback({ cancel: false });
    },
  );

  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
