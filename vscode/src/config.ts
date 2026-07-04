import * as vscode from 'vscode';

export type WatchLlmMode = 'enforce' | 'shadow';

export interface WatchLlmConfig {
    pythonPath: string;
    kernelPath: string;
    mode: WatchLlmMode;
}

export const DEFAULT_WATCHLLM_CONFIG: WatchLlmConfig = {
    pythonPath: 'python',
    kernelPath: '-m watchllm_kernel evaluate',
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

export function getWatchLlmConfig(): WatchLlmConfig {
    const section = vscode.workspace.getConfiguration('watchllm');

    return {
        pythonPath: readNonEmptyString(section, 'pythonPath', DEFAULT_WATCHLLM_CONFIG.pythonPath),
        kernelPath: readNonEmptyString(section, 'kernelPath', DEFAULT_WATCHLLM_CONFIG.kernelPath),
        mode: readMode(section)
    };
}
