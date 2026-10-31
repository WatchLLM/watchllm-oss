const express = require('express');
const crypto = require('crypto');
const { db, dbPath } = require('./db.cjs');

const app = express();
const port = Number(process.env.PORT || 3001);

app.use(express.json());

function randomId(prefix) {
  return `${prefix}_${crypto.randomUUID()}`;
}

function toJsonText(value, fallback = null) {
  if (value === undefined) {
    return fallback;
  }

  if (typeof value === 'string') {
    return value;
  }

  return JSON.stringify(value);
}

function parseJsonText(value, fallback = null) {
  if (value === null || value === undefined) {
    return fallback;
  }

  try {
    return JSON.parse(value);
  } catch {
    return value;
  }
}

function mapRun(row) {
  if (!row) return null;
  return {
    id: row.id,
    name: row.name,
    metadata: parseJsonText(row.metadata, {}),
    createdAt: row.created_at,
  };
}

function mapStepNode(row) {
  if (!row) return null;
  return {
    id: row.id,
    runId: row.run_id,
    sequence: row.sequence,
    type: row.type,
    label: row.label,
    toolName: row.tool_name,
    input: parseJsonText(row.input),
    output: parseJsonText(row.output),
    stateBefore: parseJsonText(row.state_before),
    stateAfter: parseJsonText(row.state_after),
    createdAt: row.created_at,
  };
}

function mapEdge(row) {
  if (!row) return null;
  return {
    id: row.id,
    runId: row.run_id,
    sourceStepId: row.source_step_id,
    targetStepId: row.target_step_id,
    relationship: row.relationship,
    createdAt: row.created_at,
  };
}

app.get('/health', (_req, res) => {
  res.json({
    ok: true,
    service: 'watchllm-replay-backend',
    dbPath,
  });
});

app.get('/', (_req, res) => {
  res.json({
    name: 'WatchLLM Replay Backend',
    status: 'running',
  });
});

app.post('/api/runs', (req, res) => {
  const id = req.body.id || randomId('run');
  const name = req.body.name || null;
  const metadata = toJsonText(req.body.metadata, '{}');

  try {
    db.prepare(`
      INSERT INTO runs (id, name, metadata)
      VALUES (?, ?, ?)
    `).run(id, name, metadata);

    const run = db.prepare(`
      SELECT id, name, metadata, created_at
      FROM runs
      WHERE id = ?
    `).get(id);

    return res.status(201).json({
      run: mapRun(run),
    });
  } catch (error) {
    if (String(error.message).includes('UNIQUE')) {
      return res.status(409).json({
        error: 'Run already exists',
        details: error.message,
      });
    }

    return res.status(500).json({
      error: 'Failed to create run',
      details: error.message,
    });
  }
});

app.post('/api/runs/:runId/steps', (req, res) => {
  const { runId } = req.params;

  const run = db.prepare(`
    SELECT id
    FROM runs
    WHERE id = ?
  `).get(runId);

  if (!run) {
    return res.status(404).json({
      error: 'Run not found',
    });
  }

  if (!req.body.type) {
    return res.status(400).json({
      error: 'Step type is required',
    });
  }

  const createStep = db.transaction(() => {
    const nextSequenceRow = db.prepare(`
      SELECT COALESCE(MAX(sequence), 0) + 1 AS next_sequence
      FROM steps
      WHERE run_id = ?
    `).get(runId);

    const id = req.body.id || randomId('step');
    const sequence = req.body.sequence ?? nextSequenceRow.next_sequence;

    const step = {
      id,
      run_id: runId,
      sequence,
      type: req.body.type,
      label: req.body.label || null,
      tool_name: req.body.toolName || req.body.tool_name || null,
      input: toJsonText(req.body.input),
      output: toJsonText(req.body.output),
      state_before: toJsonText(req.body.stateBefore ?? req.body.state_before),
      state_after: toJsonText(req.body.stateAfter ?? req.body.state_after),
    };

    db.prepare(`
      INSERT INTO steps (
        id,
        run_id,
        sequence,
        type,
        label,
        tool_name,
        input,
        output,
        state_before,
        state_after
      )
      VALUES (
        @id,
        @run_id,
        @sequence,
        @type,
        @label,
        @tool_name,
        @input,
        @output,
        @state_before,
        @state_after
      )
    `).run(step);

    const sourceStepIds = [];

    if (req.body.parentStepId) {
      sourceStepIds.push(req.body.parentStepId);
    }

    if (req.body.sourceStepId) {
      sourceStepIds.push(req.body.sourceStepId);
    }

    if (Array.isArray(req.body.sourceStepIds)) {
      sourceStepIds.push(...req.body.sourceStepIds);
    }

    const uniqueSourceStepIds = [...new Set(sourceStepIds)];

    const insertEdge = db.prepare(`
      INSERT INTO edges (
        run_id,
        source_step_id,
        target_step_id,
        relationship
      )
      VALUES (?, ?, ?, ?)
    `);

    for (const sourceStepId of uniqueSourceStepIds) {
      insertEdge.run(
        runId,
        sourceStepId,
        id,
        req.body.relationship || 'next'
      );
    }

    return db.prepare(`
      SELECT
        id,
        run_id,
        sequence,
        type,
        label,
        tool_name,
        input,
        output,
        state_before,
        state_after,
        created_at
      FROM steps
      WHERE id = ?
    `).get(id);
  });

  try {
    const step = createStep();

    return res.status(201).json({
      step: mapStepNode(step),
    });
  } catch (error) {
    if (String(error.message).includes('UNIQUE')) {
      return res.status(409).json({
        error: 'Step already exists or sequence already used',
        details: error.message,
      });
    }

    if (String(error.message).includes('FOREIGN KEY')) {
      return res.status(400).json({
        error: 'Invalid step relationship',
        details: error.message,
      });
    }

    return res.status(500).json({
      error: 'Failed to create step',
      details: error.message,
    });
  }
});

// Query API

app.get('/api/runs', (_req, res) => {
  try {
    const rows = db.prepare(`
      SELECT id, name, metadata, created_at
      FROM runs
      ORDER BY created_at DESC
    `).all();

    const runs = rows.map(mapRun);

    return res.json({ runs });
  } catch (error) {
    return res.status(500).json({
      error: 'Failed to fetch runs',
      details: error.message,
    });
  }
});

app.get('/api/runs/:runId/graph', (req, res) => {
  const { runId } = req.params;

  const run = db.prepare(`
    SELECT id, name, metadata, created_at
    FROM runs
    WHERE id = ?
  `).get(runId);

  if (!run) {
    return res.status(404).json({
      error: 'Run not found',
    });
  }

  try {
    const stepRows = db.prepare(`
      SELECT
        id,
        run_id,
        sequence,
        type,
        label,
        tool_name,
        input,
        output,
        state_before,
        state_after,
        created_at
      FROM steps
      WHERE run_id = ?
      ORDER BY sequence ASC
    `).all(runId);

    const edgeRows = db.prepare(`
      SELECT
        id,
        run_id,
        source_step_id,
        target_step_id,
        relationship,
        created_at
      FROM edges
      WHERE run_id = ?
    `).all(runId);

    const nodes = stepRows.map(mapStepNode);
    const edges = edgeRows.map(mapEdge);

    return res.json({
      run: mapRun(run),
      nodes,
      edges,
    });
  } catch (error) {
    return res.status(500).json({
      error: 'Failed to fetch graph',
      details: error.message,
    });
  }
});

if (require.main === module) {
  app.listen(port, () => {
    console.log(`WatchLLM Replay backend listening on http://localhost:${port}`);
    console.log(`SQLite database initialised at ${dbPath}`);
  });
}

module.exports = { app };
