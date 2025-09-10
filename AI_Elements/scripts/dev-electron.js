/**
 * Next.js開発サーバとElectronを同時起動する簡易スクリプト。
 * - 先にnext devを立ち上げ、一定時間後にElectronを起動
 * - `APP_START_URL` を http://localhost:3000 に設定
 */
const { spawn } = require('node:child_process');

const NEXT_PORT = process.env.PORT || '3000';
const APP_URL = `http://localhost:${NEXT_PORT}`;

const next = spawn(process.platform === 'win32' ? 'npx.cmd' : 'npx', ['next', 'dev', 'apps/web', '-p', NEXT_PORT], {
  stdio: 'inherit',
  env: { ...process.env, NEXT_TELEMETRY_DISABLED: '1' },
});

setTimeout(() => {
  const env = { ...process.env, APP_START_URL: APP_URL };
  const electron = spawn(process.platform === 'win32' ? 'npx.cmd' : 'npx', ['electron', '--no-sandbox', '.'], { stdio: 'inherit', env });
  electron.on('exit', (code) => {
    next.kill('SIGTERM');
    process.exit(code ?? 0);
  });
}, 3000);

process.on('SIGINT', () => { next.kill('SIGINT'); process.exit(0); });

