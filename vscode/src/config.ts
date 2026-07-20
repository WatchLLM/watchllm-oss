import * as vscode from 'vscode';

export type WatchLlmMode = 'enforce' | 'shadow';

export interface WatchLlmConfig {
    pythonPath: string;
    kernelPath: string;
    /** Absolute path to the watchllm-cli Rust binary. When set, the extension
     *  will prefer the Rust runtime over the Python kernel subprocess. */
    rustCliPath: string | null;
    mode: WatchLlmMode;
}

export const DEFAULT_WATCHLLM_CONFIG: WatchLlmConfig = {
    pythonPath: 'python',
    kernelPath: '-m watchllm_kernel check',
    rustCliPath: null,
    mode: 'enforce'
};

function readNonEmptyString(
    section: vscode.WorkspaceConfiguration,
    key: keyof Pick<WatchLlmConfig, 'pythonPath' | 'kernelPath'>,
    fallback: string
): string {
    const value = section.get<unknown>(key);

    if (typeof value !== 'string') {
        return fallback;
    }

    const trimmed = value.trim();
    return trimmed.length > 0 ? trimmed : fallback;
}

function readMode(section: vscode.WorkspaceConfiguration): WatchLlmMode {
    const value = section.get<unknown>('mode');

    if (value === 'enforce' || value === 'shadow') {
        return value;
    }

    return DEFAULT_WATCHLLM_CONFIG.mode;
}

function readNullableString(
    section: vscode.WorkspaceConfiguration,
    key: string,
): string | null {
    const value = section.get<unknown>(key);
    if (typeof value !== 'string') {
        return null;
    }
    const trimmed = value.trim();
    return trimmed.length > 0 ? trimmed : null;
}

export function getWatchLlmConfig(): WatchLlmConfig {
    const section = vscode.workspace.getConfiguration('watchllm');

    return {
        pythonPath: readNonEmptyString(section, 'pythonPath', DEFAULT_WATCHLLM_CONFIG.pythonPath),
        kernelPath: readNonEmptyString(section, 'kernelPath', DEFAULT_WATCHLLM_CONFIG.kernelPath),
        rustCliPath: readNullableString(section, 'rustCliPath'),
        mode: readMode(section)
    };
}
