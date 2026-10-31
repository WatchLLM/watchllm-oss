import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

type Run = {
  id: string;
  name: string | null;
  metadata: unknown;
  createdAt: string;
};

function RunsList() {
  const [runs, setRuns] = useState<Run[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchRuns() {
      try {
        const response = await fetch('/api/runs');
        if (!response.ok) {
          throw new Error(`Server responded with ${response.status}`);
        }
        const data = await response.json();
        if (!cancelled) {
          setRuns(data.runs ?? []);
          setLoading(false);
        }
      } catch (err: unknown) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to fetch runs');
          setLoading(false);
        }
      }
    }

    fetchRuns();

    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return <div className="state-message">Loading runs…</div>;
  }

  if (error) {
    return <div className="error-message">Error: {error}</div>;
  }

  if (runs.length === 0) {
    return <div className="state-message">No runs found. Ingest a run to see it here.</div>;
  }

  return (
    <div>
      <h1 className="page-header">Runs</h1>
      <div className="runs-grid">
        {runs.map((run) => (
          <Link key={run.id} className="run-card run-card-link" to={`/runs/${run.id}`}>
            <h3>{run.name ?? 'Untitled run'}</h3>
            <p className="run-meta">
              <strong>ID:</strong> {run.id}
            </p>
            <p className="run-meta">
              <strong>Created:</strong> {new Date(run.createdAt).toLocaleString()}
            </p>
            <div className="metadata-preview">
              <strong>Metadata</strong>
              <pre>{JSON.stringify(run.metadata, null, 2)}</pre>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}

export default RunsList;
