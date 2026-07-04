import * as vscode from 'vscode';

export interface KernelViolation {
    message: string;
    line: number;   // 1‑based
    column: number; // 1‑based
    severity?: 'error' | 'warning' | 'info';
}

export interface KernelResultPayload {
    violations?: KernelViolation[];
}

interface NormalizedViolation {
    message: string;
    line: number;
    column: number;
    severity?: string;
}

function extractViolations(payload: unknown): NormalizedViolation[] {
    if (!payload || typeof payload !== 'object') {
        return [];
    }

    const rawPayload = payload as Record<string, unknown>;
    const violations: NormalizedViolation[] = [];

    // 1. Check if it's the Rust CLI/Wasm output format (nested inside payload object)
    if (rawPayload.status === 'ok' && rawPayload.payload && typeof rawPayload.payload === 'object') {
        const innerPayload = rawPayload.payload as Record<string, unknown>;
        if (Array.isArray(innerPayload.violations)) {
            for (const v of innerPayload.violations) {
                if (v && typeof v === 'object') {
                    const rawV = v as Record<string, unknown>;
                    violations.push({
                        message: typeof rawV.message === 'string' ? rawV.message : 'WatchLLM policy violation',
                        line: typeof rawV.line === 'number' ? rawV.line : 1,
                        column: typeof rawV.column === 'number' ? rawV.column : 1,
                        severity: typeof rawV.severity === 'string' ? rawV.severity : 'error'
                    });
                }
            }
            return violations;
        }
    }

    // 2. Check if it has a flat violations array (like canonical schema or mock)
    if (Array.isArray(rawPayload.violations)) {
        for (const v of rawPayload.violations) {
            if (v && typeof v === 'object') {
                const rawV = v as Record<string, unknown>;
                let line = 1;
                let column = 1;
                if (rawV.location && typeof rawV.location === 'object') {
                    const loc = rawV.location as Record<string, unknown>;
                    line = typeof loc.line === 'number' ? loc.line : 1;
                    column = typeof loc.column === 'number' ? loc.column : 1;
                } else {
                    line = typeof rawV.line === 'number' ? rawV.line : 1;
                    column = typeof rawV.column === 'number' ? rawV.column : 1;
                }
                violations.push({
                    message: typeof rawV.message === 'string' ? rawV.message : 'WatchLLM policy violation',
                    line,
                    column,
                    severity: typeof rawV.severity === 'string' ? rawV.severity : 'error'
                });
            }
        }
        return violations;
    }

    // 3. Check if it's the Python CLI format (nested in rule_results)
    if (Array.isArray(rawPayload.rule_results)) {
        for (const rr of rawPayload.rule_results) {
            if (rr && typeof rr === 'object') {
                const rawRr = rr as Record<string, unknown>;
                if (Array.isArray(rawRr.violations)) {
                    for (const v of rawRr.violations) {
                        if (v && typeof v === 'object') {
                            const rawV = v as Record<string, unknown>;
                            let line = 1;
                            let column = 1;
                            if (rawV.location && typeof rawV.location === 'object') {
                                const loc = rawV.location as Record<string, unknown>;
                                line = typeof loc.line === 'number' ? loc.line : 1;
                                column = typeof loc.column === 'number' ? loc.column : 1;
                            } else {
                                line = typeof rawV.line === 'number' ? rawV.line : 1;
                                column = typeof rawV.column === 'number' ? rawV.column : 1;
                            }
                            violations.push({
                                message: typeof rawV.message === 'string' ? rawV.message : 'WatchLLM policy violation',
                                line,
                                column,
                                severity: typeof rawV.severity === 'string' ? rawV.severity : 'error'
                            });
                        }
                    }
                }
            }
        }
        return violations;
    }

    return [];
}

/**
 * Convert a kernel JSON payload into VS Code Diagnostic objects.
 * Returns an empty array if the payload is missing or malformed.
 */
export function mapViolationsToDiagnostics(
    payload: unknown,
    document: vscode.TextDocument
): vscode.Diagnostic[] {
    const violations = extractViolations(payload);
    const diagnostics: vscode.Diagnostic[] = [];

    for (const v of violations) {
        // VS Code positions are 0‑based
        const zeroBasedLine = Math.max(0, v.line - 1);
        const zeroBasedColumn = Math.max(0, v.column - 1);

        // Clamp to document range to avoid out‑of‑bounds errors
        const maxLine = document.lineCount - 1;
        const clampedLine = Math.min(zeroBasedLine, maxLine);
        const lineText = document.lineAt(clampedLine).text;
        const clampedColumn = Math.min(zeroBasedColumn, lineText.length);

        const range = new vscode.Range(
            clampedLine,
            clampedColumn,
            clampedLine,
            clampedColumn
        );

        const severity = mapSeverity(v.severity);
        const diagnostic = new vscode.Diagnostic(range, v.message, severity);
        diagnostic.source = 'WatchLLM';
        diagnostics.push(diagnostic);
    }

    return diagnostics;
}

function mapSeverity(severity?: string): vscode.DiagnosticSeverity {
    if (!severity) {
        return vscode.DiagnosticSeverity.Error;
    }

    const lower = severity.toLowerCase();
    switch (lower) {
        case 'critical':
        case 'high':
        case 'error':
            return vscode.DiagnosticSeverity.Error;
        case 'medium':
        case 'warning':
            return vscode.DiagnosticSeverity.Warning;
        case 'low':
        case 'info':
        default:
            return vscode.DiagnosticSeverity.Information;
    }
}

/**
 * Create a DiagnosticCollection that will be used to show violations.
 */
export function createDiagnosticCollection(): vscode.DiagnosticCollection {
    return vscode.languages.createDiagnosticCollection('watchllm');
}
