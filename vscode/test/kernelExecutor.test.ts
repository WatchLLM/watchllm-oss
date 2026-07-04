import { strict as assert } from 'assert';
import * as path from 'path';
import { test } from 'node:test';
import { runKernelCheck } from '../src/kernelExecutor';
import type { WatchLlmConfig } from '../src/config';

function fixturePath(): string {
    return path.resolve(__dirname, '../../test/fixtures/dummy-kernel.js');
}

function configFor(extraKernelArgs: string): WatchLlmConfig {
    return {
        pythonPath: process.execPath,
        kernelPath: `"${fixturePath()}" ${extraKernelArgs}`,
        mode: 'enforce'
    };
}

test('runKernelCheck parses JSON stdout for exit code 0', async () => {
    const result = await runKernelCheck({
        config: configFor('--exit 0'),
        documentText: 'const value = 1;',
        language: 'typescript',
        timeoutMs: 1_000
    });

    assert.equal(result.status, 'completed');
    assert.equal(result.exitCode, 0);
    assert.equal(typeof result.json, 'object');

    const json = result.json as { exitCode: number; language: string; mode: string; stdin: string };

    assert.equal(json.exitCode, 0);
    assert.equal(json.language, 'typescript');
    assert.equal(json.mode, 'enforce');
    assert.equal(json.stdin, 'const value = 1;');
});

test('runKernelCheck parses JSON stdout for exit code 1', async () => {
    const result = await runKernelCheck({
        config: configFor('--exit 1'),
        documentText: 'secret',
        language: 'javascript',
        timeoutMs: 1_000
    });

    assert.equal(result.status, 'completed');
    assert.equal(result.exitCode, 1);

    const json = result.json as { exitCode: number; stdin: string };

    assert.equal(json.exitCode, 1);
    assert.equal(json.stdin, 'secret');
});

test('runKernelCheck parses JSON stdout for exit code 2', async () => {
    const result = await runKernelCheck({
        config: configFor('--exit 2'),
        documentText: 'broken infrastructure case',
        language: 'typescript',
        timeoutMs: 1_000
    });

    assert.equal(result.status, 'completed');
    assert.equal(result.exitCode, 2);

    const json = result.json as { exitCode: number };

    assert.equal(json.exitCode, 2);
});

test('runKernelCheck enforces timeout', async () => {
    const result = await runKernelCheck({
        config: configFor('--exit 0 --sleep-ms 500'),
        documentText: 'slow',
        language: 'typescript',
        timeoutMs: 50
    });

    assert.equal(result.status, 'timeout');
    assert.equal(result.json, null);
    assert.match(result.errorMessage ?? '', /timed out/i);
});
