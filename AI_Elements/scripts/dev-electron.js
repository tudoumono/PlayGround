/**
 * Next.js開発サーバとElectronを同時起動する簡易スクリプト。
 * - 先にnext devを立ち上げ、一定時間後にElectronを起動
 * - `APP_START_URL` を http://localhost:3000 に設定
 */
const { spawn } = require('node:child_process');
const path = require('node:path');
const fs = require('node:fs');

function bin(cmd) {
  const ext = process.platform === 'win32' ? '.cmd' : '';
  return path.resolve(__dirname, '..', 'node_modules', '.bin', cmd + ext);
}

function spawnCmd(binPath, args, opts) {
  const isWin = process.platform === 'win32';
  if (isWin) {
    // Windowsでの EINVAL 回避: cmd.exe 経由で起動
    const quoted = /\s/.test(binPath) ? `"${binPath}"` : binPath;
    return spawn('cmd.exe', ['/c', quoted, ...args], opts);
  }
  return spawn(binPath, args, opts);
}

const NEXT_PORT = process.env.PORT || '3000';
const APP_URL = `http://localhost:${NEXT_PORT}`;

const nextBin = bin('next');
if (!fs.existsSync(nextBin)) {
  console.error('[dev-electron] next bin not found:', nextBin);
}
const next = spawnCmd(nextBin, ['dev', 'apps/web', '-p', NEXT_PORT], {
  stdio: 'inherit',
  env: { ...process.env, NEXT_TELEMETRY_DISABLED: '1' },
});

setTimeout(() => {
  const env = { ...process.env, APP_START_URL: APP_URL };
  const electronBin = bin('electron');
  if (!fs.existsSync(electronBin)) {
    console.error('[dev-electron] electron bin not found:', electronBin);
  }
  const electron = spawnCmd(electronBin, ['--no-sandbox', '.'], { stdio: 'inherit', env });
  electron.on('exit', (code) => {
    next.kill('SIGTERM');
    process.exit(code ?? 0);
  });
}, 3000);

process.on('SIGINT', () => { next.kill('SIGINT'); process.exit(0); });
