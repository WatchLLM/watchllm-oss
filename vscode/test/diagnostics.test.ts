import { strict as assert } from 'assert';
import { test } from 'node:test';
import Module = require('module');

// -----------------------------------------------------------------------------
// Register VS Code Mock
// -----------------------------------------------------------------------------
class Position {
    constructor(public readonly line: number, public readonly character: number) {}
}

class Range {
    public readonly start: Position;
    public readonly end: Position;
    constructor(startLine: number, startColumn: number, endLine: number, endColumn: number) {
        this.start = new Position(startLine, startColumn);
        this.end = new Position(endLine, endColumn);
    }
}

const vscodeMock = {
    Position,
    Range,
    Diagnostic: class Diagnostic {
        public source: string = '';
        constructor(
            public range: Range,
            public message: string,
            public severity: number
        ) {}
    },
    DiagnosticSeverity: {
        Error: 0,
        Warning: 1,
        Information: 2,
        Hint: 3
    },
    languages: {
        createDiagnosticCollection: (name: string) => ({
            name,
            delete: () => {},
            set: () => {},
            dispose: () => {}
        })
    }
};

const originalResolveFilename = (Module as any)._resolveFilename;
(Module as any)._resolveFilename = function (request: string, ...args: any[]) {
    if (request === 'vscode') {
        return 'vscode';
    }
    return originalResolveFilename.apply(this, [request, ...args]);
};

const mockModule = new Module('vscode', module.parent || undefined);
mockModule.exports = vscodeMock;
(Module as any)._cache['vscode'] = mockModule;

// Import the module under test after registering the mock
const { mapViolationsToDiagnostics } = require('../src/diagnostics');

// -----------------------------------------------------------------------------
// Helpers
// -----------------------------------------------------------------------------
function documentOf(lines: string[]): any {
    return {
        lineCount: lines.length,
        lineAt: (index: number) => {
            const text = lines[index] || '';
            return { text };
        }
    };
}

// -----------------------------------------------------------------------------
// Test Cases
// -----------------------------------------------------------------------------

test('mapViolationsToDiagnostics parses Python CLI format with rule_results', () => {
    const pythonPayload = {
        decision: 'BLOCK',
        rule_results: [
            {
                rule_id: 'SECRET_LITERAL',
                decision: 'FAIL',
                violations: [
                    {
                        rule_id: 'SECRET_LITERAL',
                        message: 'Hardcoded secret found',
                        location: {
                            line: 2,
                            column: 5
                        },
                        severity: 'HIGH'
                    }
                ]
            },
            {
                rule_id: 'FORBIDDEN_IMPORT',
                decision: 'PASS',
                violations: []
            }
        ]
    };

    const doc = documentOf(['const x = 1;', 'const secret = "sk_live_123";']);
    const diags = mapViolationsToDiagnostics(pythonPayload, doc);

    assert.equal(diags.length, 1);
    assert.equal(diags[0].message, 'Hardcoded secret found');
    assert.equal(diags[0].severity, 0); // DiagnosticSeverity.Error
    assert.equal(diags[0].range.start.line, 1); // 0-based
    assert.equal(diags[0].range.start.character, 4); // 0-based
});

test('mapViolationsToDiagnostics parses Rust CLI/Wasm format with status & payload.violations', () => {
    const rustPayload = {
        status: 'ok',
        exit_code: 1,
        payload: {
            allowed: false,
            violations: [
                {
                    message: 'Forbidden import: fs',
                    rule: 'imports',
                    line: 1,
                    column: 1,
                    severity: 'warning'
                }
            ]
        }
    };

    const doc = documentOf(['import * as fs from "fs";']);
    const diags = mapViolationsToDiagnostics(rustPayload, doc);

    assert.equal(diags.length, 1);
    assert.equal(diags[0].message, 'Forbidden import: fs');
    assert.equal(diags[0].severity, 1); // DiagnosticSeverity.Warning
    assert.equal(diags[0].range.start.line, 0); // 0-based
    assert.equal(diags[0].range.start.character, 0); // 0-based
});

test('mapViolationsToDiagnostics parses canonical flat violations format', () => {
    const canonicalPayload = {
        decision: 'BLOCK',
        violations: [
            {
                message: 'Cross boundary access',
                line: 3,
                column: 8,
                severity: 'info'
            }
        ]
    };

    const doc = documentOf(['line 1', 'line 2', 'boundary_check()']);
    const diags = mapViolationsToDiagnostics(canonicalPayload, doc);

    assert.equal(diags.length, 1);
    assert.equal(diags[0].message, 'Cross boundary access');
    assert.equal(diags[0].severity, 2); // DiagnosticSeverity.Information
    assert.equal(diags[0].range.start.line, 2); // 0-based
    assert.equal(diags[0].range.start.character, 7); // 0-based
});

test('mapViolationsToDiagnostics returns empty array on empty or malformed input', () => {
    const doc = documentOf(['line 1']);
    assert.deepEqual(mapViolationsToDiagnostics(null, doc), []);
    assert.deepEqual(mapViolationsToDiagnostics({}, doc), []);
    assert.deepEqual(mapViolationsToDiagnostics('not an object', doc), []);
});
