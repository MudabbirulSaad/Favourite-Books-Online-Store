import { readdir } from 'node:fs/promises';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';

async function jsFiles(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const files = await Promise.all(entries.map(async entry => {
    const path = join(directory, entry.name);
    if (entry.isDirectory()) return jsFiles(path);
    return path.endsWith('.js') ? [path] : [];
  }));
  return files.flat();
}

for (const file of await jsFiles('frontend')) {
  const result = spawnSync(process.execPath, ['--check', file], { stdio: 'inherit' });
  if (result.status !== 0) {
    process.exit(result.status);
  }
}

console.log('frontend syntax: ok');
