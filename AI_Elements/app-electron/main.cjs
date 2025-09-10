/**
 * Electron メイン（CommonJS版）
 * - TypeScriptビルドに依存せず、常に`electron`を正しく解決させるためのエントリ
 */
const { app, BrowserWindow, session } = require('electron');
let bootstrap;
try {
  bootstrap = require('../dist/src/server/bootstrap.js').bootstrap;
} catch (e) {
  // ネイティブDBが使えない場合はSAFE_MODEで起動（DB無効、ENVのみ）
  process.env.SAFE_MODE = 'true';
  bootstrap = () => {};
}

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
  win.loadURL(process.env.APP_START_URL || 'about:blank');
}

app.whenReady().then(() => {
  bootstrap();
  session.defaultSession.webRequest.onBeforeRequest((_details, callback) => callback({ cancel: false }));
  createWindow();
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
