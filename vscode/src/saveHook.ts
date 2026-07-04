import {
    runKernelCheck,
    type KernelExecutionRequest,
    type KernelExecutionResult
} from './kernelExecutor';
import type { WatchLlmConfig } from './config';

export interface SaveCheckDocument {
    languageId: string;
    getText(): string;
    uri: { fsPath: string; toString(): string };
}

export type KernelRunner = (request: KernelExecutionRequest) => Promise<KernelExecutionResult>;

const SUPPORTED_LANGUAGES = new Set(['javascript', 'typescript']);

export interface SaveCheckResult {
    /** Whether the save should be allowed. */
    allowed: boolean;
    /** Kernel execution result (may be null if the language is unsupported). */
    kernelResult: KernelExecutionResult | null;
    /** Parsed kernel JSON payload (may be null). */
    payload: unknown;
}

/**
 * Run the kernel check for a document and return a structured result.
 *
 * This function does NOT import vscode. It is a pure logic layer.
 * The caller (extension.ts) is responsible for diagnostics, notifications,
 * and deciding whether to block the save.
 */
export async function checkDocumentBeforeSave(
    document: SaveCheckDocument,
    config: WatchLlmConfig,
    runner: KernelRunner = runKernelCheck
): Promise<SaveCheckResult> {
    if (!SUPPORTED_LANGUAGES.has(document.languageId)) {
        return {
            allowed: true,
            kernelResult: null,
            payload: null
        };
    }

    let result: KernelExecutionResult;

    try {
        result = await runner({
            config,
            documentText: document.getText(),
            language: document.languageId
        });
    } catch {
        // Fail open if the executor unexpectedly throws.
        return {
            allowed: true,
            kernelResult: null,
            payload: null
        };
    }

    // Parse kernel stdout
    let payload: unknown = null;
    if (result.status === 'completed' && result.stdout) {
        try {
            payload = JSON.parse(result.stdout);
        } catch {
            // Malformed JSON – treat as no violations
        }
    }

    // Determine whether the save should be blocked
    let allowed = true;

    if (result.status === 'completed' && result.exitCode === 1) {
        if (config.mode === 'enforce') {
            allowed = false;
        }
        // In shadow mode we do not block the save
    } else if (result.status === 'completed' && result.exitCode === 2) {
        // Kernel error – fail open
        allowed = true;
    } else if (result.status === 'timeout') {
        // Timeout – fail open
        allowed = true;
    }

    return {
        allowed,
        kernelResult: result,
        payload
    };
}
