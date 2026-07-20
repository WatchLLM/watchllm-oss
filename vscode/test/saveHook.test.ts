import { strict as assert } from 'assert';
import { test } from 'node:test';
import {
    checkDocumentBeforeSave,
    type SaveCheckDocument,
    type KernelRunner
} from '../src/saveHook';
import type { WatchLlmConfig } from '../src/config';
import type { KernelExecutionResult } from '../src/kernelExecutor';

const baseConfig: WatchLlmConfig = {
    pythonPath: 'python',
    kernelPath: '-m watchllm_kernel check',
    mode: 'enforce',
    rustCliPath: null
};

function document(languageId: string, text: string): SaveCheckDocument {
    return {
        languageId,
        getText: () => text,
        uri: {
            fsPath: '/fake/path.ts',
            toString: () => 'file:///fake/path.ts'
        }
    };
}

function result(exitCode: number): KernelExecutionResult {
    return {
        status: 'completed',
        exitCode,
        signal: null,
        stdout: '{}',
        stderr: '',
        json: {}
    };
}

test('checkDocumentBeforeSave allows save when kernel exits 0', async () => {
    let called = false;

    const runner: KernelRunner = async (request) => {
        called = true;
        assert.equal(request.documentText, 'const value = 1;');
        assert.equal(request.language, 'typescript');
        assert.equal(request.config.mode, 'enforce');

        return result(0);
    };

    await checkDocumentBeforeSave(
        document('typescript', 'const value = 1;'),
        baseConfig,
        runner
    );

    assert.equal(called, true);
});

test('checkDocumentBeforeSave blocks save when kernel exits 1', async () => {
    const runner: KernelRunner = async () => result(1);

    const saveResult = await checkDocumentBeforeSave(
        document('javascript', 'const secret = "abc";'),
        baseConfig,
        runner
    );

    assert.equal(saveResult.allowed, false);
});

test('checkDocumentBeforeSave allows save when kernel exits 2', async () => {
    const runner: KernelRunner = async () => result(2);

    await checkDocumentBeforeSave(
        document('typescript', 'infrastructure failure case'),
        baseConfig,
        runner
    );
});

test('checkDocumentBeforeSave allows save for executor timeout status', async () => {
    const runner: KernelRunner = async () => ({
        status: 'timeout',
        exitCode: null,
        signal: null,
        stdout: '',
        stderr: '',
        json: null,
        errorMessage: 'Kernel timed out.'
    });

    await checkDocumentBeforeSave(
        document('typescript', 'slow file'),
        baseConfig,
        runner
    );
});

test('checkDocumentBeforeSave skips unsupported languages', async () => {
    let called = false;

    const runner: KernelRunner = async () => {
        called = true;
        return result(1);
    };

    await checkDocumentBeforeSave(
        document('python', 'print("not handled by this extension")'),
        baseConfig,
        runner
    );

    assert.equal(called, false);
});

test('checkDocumentBeforeSave fails open if runner throws unexpectedly', async () => {
    const runner: KernelRunner = async () => {
        throw new Error('unexpected executor failure');
    };

    await checkDocumentBeforeSave(
        document('typescript', 'const value = 1;'),
        baseConfig,
        runner
    );
});
