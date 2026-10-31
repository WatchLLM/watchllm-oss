const { test } = require('node:test');
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');

test('frontend builds successfully', () => {
  const result = spawnSync('npm', ['run', 'build:frontend'], {
    stdio: 'pipe',
    shell: process.platform === 'win32',
    encoding: 'utf8',
  });

  assert.strictEqual(
    result.status,
    0,
    `frontend build failed\nSTDOUT:\n${result.stdout}\nSTDERR:\n${result.stderr}`
  );
});
