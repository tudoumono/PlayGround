/**
 * UI静的アセットを dist/ui へコピーするビルド後スクリプト。
 * - Next.js未導入の現段階では、シンプルな静的UIでElectronに表示させる。
 */
const fs = require('node:fs');
const path = require('node:path');

const srcDir = path.resolve(__dirname, '..', 'ui');
const outDir = path.resolve(__dirname, '..', 'dist', 'ui');

function copyDir(src, dst) {
  if (!fs.existsSync(src)) return;
  fs.mkdirSync(dst, { recursive: true });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const s = path.join(src, entry.name);
    const d = path.join(dst, entry.name);
    if (entry.isDirectory()) copyDir(s, d);
    else fs.copyFileSync(s, d);
  }
}

copyDir(srcDir, outDir);
console.log(`[copy-ui] Copied UI assets to ${outDir}`);

