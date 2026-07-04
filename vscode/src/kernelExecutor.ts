import { spawn } from 'child_process';
import type { WatchLlmConfig } from './config';

export interface KernelExecutionRequest {
    config: WatchLlmConfig;
    documentText: string;
    language: string;
    timeoutMs?: number;
}

export type KernelExecutionStatus =
    | 'completed'
    | 'malformedJson'
    | 'timeout'
    | 'spawnError';

export interface KernelExecutionResult {
    status: KernelExecutionStatus;
    exitCode: number | null;
    signal: NodeJS.Signals | null;
    stdout: string;
    stderr: string;
    json: unknown | null;
    errorMessage?: string;
}

const DEFAULT_TIMEOUT_MS = 5_000;

function splitArgs(input: string): string[] {
    const args: string[] = [];
    let current = '';
    let quote: '"' | "'" | null = null;

    for (let index = 0; index < input.length; index += 1) {
        const char = input[index];

        if (quote !== null) {
            if (char === quote) {
                quote = null;
                continue;
            }

            current += char;
            continue;
        }

        if (char === '"' || char === "'") {
            quote = char;
            continue;
        }

        if (/\s/.test(char)) {
            if (current.length > 0) {
                args.push(current);
                current = '';
            }

            continue;
        }

        current += char;
    }

    if (quote !== null) {
        throw new Error('Unclosed quote in watchllm.kernelPath');
    }

    if (current.length > 0) {
        args.push(current);
    }

    return args;
}

function parseStdoutJson(stdout: string): { ok: true; value: unknown } | { ok: false; message: string } {
    const trimmed = stdout.trim();

    if (trimmed.length === 0) {
        return {
            ok: false,
            message: 'Kernel produced empty stdout.'
        };
    }

    try {
        return {
            ok: true,
            value: JSON.parse(trimmed)
        };
    } catch (error) {
        return {
            ok: false,
            message: error instanceof Error ? error.message : 'Failed to parse kernel stdout as JSON.'
        };
    }
}

export function runKernelCheck(request: KernelExecutionRequest): Promise<KernelExecutionResult> {
    const timeoutMs = request.timeoutMs ?? DEFAULT_TIMEOUT_MS;

    let kernelArgs: string[];

    try {
        kernelArgs = splitArgs(request.config.kernelPath);
    } catch (error) {
        return Promise.resolve({
            status: 'spawnError',
            exitCode: null,
            signal: null,
            stdout: '',
            stderr: '',
            json: null,
            errorMessage: error instanceof Error ? error.message : 'Invalid kernel configuration.'
        });
    }

    const args = [
        ...kernelArgs,
        '--stdin',
        '--json',
        '--language',
        request.language,
        '--mode',
        request.config.mode
    ];

    return new Promise<KernelExecutionResult>((resolve) => {
        let settled = false;
        let timedOut = false;
        let stdout = '';
        let stderr = '';

        const child = spawn(request.config.pythonPath, args, {
            shell: false,
            windowsHide: true,
            stdio: ['pipe', 'pipe', 'pipe']
        });

        const timeout = setTimeout(() => {
            timedOut = true;
            child.kill('SIGKILL');
        }, timeoutMs);

        const settle = (result: KernelExecutionResult): void => {
            if (settled) {
                return;
            }

            settled = true;
            clearTimeout(timeout);
            resolve(result);
        };

        child.stdout.setEncoding('utf8');
        child.stderr.setEncoding('utf8');

        child.stdout.on('data', (chunk: string) => {
            stdout += chunk;
        });

        child.stderr.on('data', (chunk: string) => {
            stderr += chunk;
        });

        child.on('error', (error) => {
            settle({
                status: 'spawnError',
                exitCode: null,
                signal: null,
                stdout,
                stderr,
                json: null,
                errorMessage: error.message
            });
        });

        child.on('close', (exitCode, signal) => {
            if (timedOut) {
                settle({
                    status: 'timeout',
                    exitCode,
                    signal,
                    stdout,
                    stderr,
                    json: null,
                    errorMessage: `Kernel timed out after ${timeoutMs}ms.`
                });
                return;
            }

            const parsed = parseStdoutJson(stdout);

            if (!parsed.ok) {
                settle({
                    status: 'malformedJson',
                    exitCode,
                    signal,
                    stdout,
                    stderr,
                    json: null,
                    errorMessage: parsed.message
                });
                return;
            }

            settle({
                status: 'completed',
                exitCode,
                signal,
                stdout,
                stderr,
                json: parsed.value
            });
        });

        child.stdin.on('error', () => {
            // The child may exit before stdin is fully written. The close/error handlers decide the final result.
        });

        child.stdin.end(request.documentText);
    });
}
