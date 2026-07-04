import * as vscode from 'vscode';
import {
    DEFAULT_WATCHLLM_CONFIG,
    getWatchLlmConfig,
    type WatchLlmConfig
} from './config';
import { checkDocumentBeforeSave } from './saveHook';
import { createDiagnosticCollection, mapViolationsToDiagnostics } from './diagnostics';

let runtimeConfig: WatchLlmConfig = DEFAULT_WATCHLLM_CONFIG;
let diagnosticCollection: vscode.DiagnosticCollection;

export function activate(context: vscode.ExtensionContext): void {
    runtimeConfig = getWatchLlmConfig();
    diagnosticCollection = createDiagnosticCollection();

    console.log(`WatchLLM extension activated. Mode: ${runtimeConfig.mode}`);

    context.subscriptions.push(
        diagnosticCollection,
        vscode.workspace.onDidChangeConfiguration((event) => {
            if (!event.affectsConfiguration('watchllm')) {
                return;
            }

            runtimeConfig = getWatchLlmConfig();
            console.log(`WatchLLM configuration updated. Mode: ${runtimeConfig.mode}`);
        }),
        vscode.workspace.onWillSaveTextDocument((event) => {
            event.waitUntil(
                (async () => {
                    const result = await checkDocumentBeforeSave(
                        event.document,
                        runtimeConfig
                    );

                    // Always clear previous diagnostics for this document
                    diagnosticCollection.delete(event.document.uri);

                    // Map kernel payload to diagnostics
                    if (result.payload) {
                        const doc = await vscode.workspace.openTextDocument(event.document.uri);
                        const diags = mapViolationsToDiagnostics(result.payload, doc);
                        if (diags.length > 0) {
                            diagnosticCollection.set(event.document.uri, diags);
                        }
                    }

                    // Show notifications based on kernel result
                    if (result.kernelResult) {
                        const kr = result.kernelResult;

                        if (kr.status === 'completed' && kr.exitCode === 1) {
                            vscode.window.showErrorMessage(
                                'WatchLLM blocked save: kernel reported a policy violation.'
                            );
                        } else if (kr.status === 'completed' && kr.exitCode === 2) {
                            vscode.window.showWarningMessage(
                                'WatchLLM kernel encountered an error. Save allowed, but please check your kernel installation.'
                            );
                        } else if (kr.status === 'timeout') {
                            vscode.window.showWarningMessage(
                                'WatchLLM kernel timed out. Save allowed, but consider increasing the timeout.'
                            );
                        }
                    }

                    // Block the save if the check determined it should be blocked
                    if (!result.allowed) {
                        throw new Error('WatchLLM blocked save: kernel reported a policy violation.');
                    }

                    return [];
                })()
            );
        })
    );
}

export function getRuntimeConfig(): WatchLlmConfig {
    return runtimeConfig;
}

export function deactivate(): void {
    // Diagnostic collection is disposed via subscriptions
}
