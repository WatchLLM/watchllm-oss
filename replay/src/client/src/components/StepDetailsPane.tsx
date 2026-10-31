import { Fragment } from 'react';

type StepDetails = {
  id: string;
  runId: string;
  sequence: number;
  type: string;
  label: string | null;
  toolName: string | null;
  input: unknown;
  output: unknown;
  stateBefore: unknown;
  stateAfter: unknown;
  createdAt: string;
};

type StepDetailsPaneProps = {
  step: StepDetails | null;
};

function formatValue(value: unknown) {
  if (value === null || value === undefined) {
    return '';
  }

  if (typeof value === 'string') {
    return value;
  }

  try {
    return JSON.stringify(value, null, 2) ?? String(value);
  } catch {
    return String(value);
  }
}

function getDiffRows(before: unknown, after: unknown) {
  const beforeLines = formatValue(before).split('\n');
  const afterLines = formatValue(after).split('\n');
  const maxLength = Math.max(beforeLines.length, afterLines.length);
  const rows = [];

  for (let index = 0; index < maxLength; index += 1) {
    const beforeLine = beforeLines[index] ?? '';
    const afterLine = afterLines[index] ?? '';

    rows.push({
      id: index,
      before: beforeLine,
      after: afterLine,
      changed: beforeLine !== afterLine,
    });
  }

  return rows;
}

function StepDetailsPane({ step }: StepDetailsPaneProps) {
  if (!step) {
    return (
      <div className="details-pane">
        <h2>Step details</h2>
        <p className="details-placeholder">
          Select a node in the graph to inspect tool arguments and state changes.
        </p>
      </div>
    );
  }

  const diffRows = getDiffRows(step.stateBefore, step.stateAfter);

  return (
    <div className="details-pane">
      <h2>
        #{step.sequence} {step.label || step.toolName || step.type}
      </h2>

      <div className="details-grid">
        <div className="details-section">
          <span className="details-section-title">Step ID</span>
          <pre>{step.id}</pre>
        </div>

        <div className="details-section">
          <span className="details-section-title">Type</span>
          <pre>{step.type}</pre>
        </div>

        {step.toolName && (
          <div className="details-section">
            <span className="details-section-title">Tool</span>
            <pre>{step.toolName}</pre>
          </div>
        )}

        <div className="details-section">
          <span className="details-section-title">Created</span>
          <pre>{new Date(step.createdAt).toLocaleString()}</pre>
        </div>

        <section className="details-section">
          <h3 className="details-section-title">Tool arguments</h3>
          <pre>{formatValue(step.input) || 'No input captured.'}</pre>
        </section>

        <section className="details-section">
          <h3 className="details-section-title">Output / logs</h3>
          <pre>{formatValue(step.output) || 'No output captured.'}</pre>
        </section>

        <section className="details-section">
          <h3 className="details-section-title">Before / After state diff</h3>

          <div className="diff-grid">
            <div className="diff-header">Before</div>
            <div className="diff-header">After</div>

            {diffRows.map((row) => (
              <Fragment key={row.id}>
                <pre
                  className={row.changed ? 'diff-line diff-line-changed' : 'diff-line'}
                >
                  {row.before || ' '}
                </pre>
                <pre
                  className={row.changed ? 'diff-line diff-line-changed' : 'diff-line'}
                >
                  {row.after || ' '}
                </pre>
              </Fragment>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

export default StepDetailsPane;
