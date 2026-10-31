import { useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import ReactFlow, {
  Background,
  Controls,
  MarkerType,
  MiniMap,
  type Edge,
  type Node,
} from 'reactflow';
import 'reactflow/dist/style.css';
import PlaybackControls from '../components/PlaybackControls';
import StepDetailsPane from '../components/StepDetailsPane';

type GraphRun = {
  id: string;
  name: string | null;
  metadata: unknown;
  createdAt: string;
};

type GraphStep = {
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

type GraphEdge = {
  id: number | string;
  runId: string;
  sourceStepId: string;
  targetStepId: string;
  relationship: string;
  createdAt: string;
};

type GraphResponse = {
  run: GraphRun;
  nodes: GraphStep[];
  edges: GraphEdge[];
};

function RunGraph() {
  const { runId } = useParams<{ runId: string }>();
  const [graph, setGraph] = useState<GraphResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [selectedStepId, setSelectedStepId] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchGraph() {
      try {
        const response = await fetch(`/api/runs/${runId}/graph`);
        if (!response.ok) {
          throw new Error(`Server responded with ${response.status}`);
        }
        const data: GraphResponse = await response.json();
        if (!cancelled) {
          setGraph(data);
          setCurrentStepIndex(0);
          setIsPlaying(false);
          setSelectedStepId(null);
          setLoading(false);
        }
      } catch (err: unknown) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to fetch graph');
          setIsPlaying(false);
          setSelectedStepId(null);
          setLoading(false);
        }
      }
    }

    fetchGraph();

    return () => {
      cancelled = true;
    };
  }, [runId]);

  const orderedSteps = useMemo(() => {
    if (!graph) return [];

    return [...graph.nodes].sort((a, b) => {
      if (a.sequence !== b.sequence) {
        return a.sequence - b.sequence;
      }

      return a.id.localeCompare(b.id);
    });
  }, [graph]);

  const activeStepId = orderedSteps[currentStepIndex]?.id ?? null;

  const selectedStep = useMemo(() => {
    if (!selectedStepId) return null;

    return orderedSteps.find((step) => step.id === selectedStepId) ?? null;
  }, [orderedSteps, selectedStepId]);

  useEffect(() => {
    if (!isPlaying || orderedSteps.length === 0) {
      return;
    }

    const timer = window.setInterval(() => {
      setCurrentStepIndex((previousIndex) => {
        if (previousIndex >= orderedSteps.length - 1) {
          setIsPlaying(false);
          return previousIndex;
        }

        const nextIndex = previousIndex + 1;

        if (nextIndex >= orderedSteps.length - 1) {
          setIsPlaying(false);
        }

        return nextIndex;
      });
    }, 1000);

    return () => {
      window.clearInterval(timer);
    };
  }, [isPlaying, orderedSteps.length]);

  function handlePlay() {
    if (orderedSteps.length === 0) {
      return;
    }

    if (currentStepIndex >= orderedSteps.length - 1) {
      setCurrentStepIndex(0);
    }

    setIsPlaying(true);
  }

  function handlePause() {
    setIsPlaying(false);
  }

  function handleStepBack() {
    setIsPlaying(false);
    setCurrentStepIndex((previousIndex) => Math.max(previousIndex - 1, 0));
  }

  function handleStepForward() {
    setIsPlaying(false);
    setCurrentStepIndex((previousIndex) =>
      Math.min(previousIndex + 1, Math.max(orderedSteps.length - 1, 0))
    );
  }

  function handleNodeClick(_event: unknown, node: Node) {
    setSelectedStepId(node.id);
  }

  const flowNodes: Node[] = useMemo(() => {
    if (!graph) return [];

    return orderedSteps.map((step, index) => ({
      id: step.id,
      position: {
        x: (index % 4) * 280,
        y: Math.floor(index / 4) * 170,
      },
      className: [
        step.id === activeStepId ? 'active-flow-node' : null,
        step.id === selectedStepId ? 'selected-flow-node' : null,
      ]
        .filter(Boolean)
        .join(' ') || undefined,
      style:
        step.id === activeStepId
          ? {
              border: '2px solid #f2cc60',
              boxShadow: '0 0 0 4px rgba(242, 204, 96, 0.24)',
            }
          : step.id === selectedStepId
            ? {
                border: '2px solid #58a6ff',
                boxShadow: '0 0 0 4px rgba(88, 166, 255, 0.2)',
              }
            : undefined,
      data: {
        label: (
          <div className="flow-node-label">
            <strong>
              #{step.sequence} {step.label || step.toolName || step.type}
            </strong>
            <span>{step.type}</span>
            {step.toolName ? <small>{step.toolName}</small> : null}
          </div>
        ),
      },
    }));
  }, [orderedSteps, activeStepId, selectedStepId]);

  const flowEdges: Edge[] = useMemo(() => {
    if (!graph) return [];

    return graph.edges.map((edge) => ({
      id: String(edge.id),
      source: edge.sourceStepId,
      target: edge.targetStepId,
      label: edge.relationship,
      markerEnd: {
        type: MarkerType.ArrowClosed,
      },
    }));
  }, [graph]);

  if (loading) {
    return <div className="state-message">Loading graph…</div>;
  }

  if (error) {
    return <div className="error-message">Error: {error}</div>;
  }

  if (!graph) {
    return <div className="error-message">Graph data not available.</div>;
  }

  if (graph.nodes.length === 0) {
    return (
      <div className="graph-page">
        <header className="graph-header">
          <Link to="/runs">← Back to runs</Link>
          <h1>{graph.run.name ?? 'Untitled run'}</h1>
        </header>
        <div className="state-message">This run has no steps yet.</div>
      </div>
    );
  }

  return (
    <div className="graph-page">
      <header className="graph-header">
        <Link to="/runs">← Back to runs</Link>
        <h1>{graph.run.name ?? 'Untitled run'}</h1>
        <p className="run-meta">
          <strong>Run ID:</strong> {graph.run.id}
        </p>
      </header>

      <PlaybackControls
        currentIndex={currentStepIndex}
        totalSteps={orderedSteps.length}
        isPlaying={isPlaying}
        onPlay={handlePlay}
        onPause={handlePause}
        onStepBack={handleStepBack}
        onStepForward={handleStepForward}
      />

      <div className="graph-details-layout">
        <div className="graph-shell">
          <ReactFlow nodes={flowNodes} edges={flowEdges} onNodeClick={handleNodeClick} fitView>
            <MiniMap />
            <Controls />
            <Background />
          </ReactFlow>
        </div>

        <StepDetailsPane step={selectedStep} />
      </div>
    </div>
  );
}

export default RunGraph;
