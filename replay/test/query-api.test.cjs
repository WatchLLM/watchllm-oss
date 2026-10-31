const { describe, it, before, after } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const request = require('supertest');

const testDbPath = path.join(
  os.tmpdir(),
  `watchllm-replay-query-api-${process.pid}-${Date.now()}.sqlite`
);

process.env.REPLAY_DB_PATH = testDbPath;

const { app } = require('../src/server/index.cjs');
const { db } = require('../src/server/db.cjs');

describe('Query API', () => {
  const uniqueSuffix = `${process.pid}-${Date.now()}`;
  const runId = `run-query-${uniqueSuffix}`;
  const firstStepId = `step-query-1-${uniqueSuffix}`;
  const integrationRunId = `run-integration-${uniqueSuffix}`;
  const integrationFirstStepId = `step-integration-1-${uniqueSuffix}`;
  const integrationSecondStepId = `step-integration-2-${uniqueSuffix}`;

  before(() => {
    // Create a run and a step so we can test graph retrieval
    db.prepare(`
      INSERT INTO runs (id, name, metadata)
      VALUES (?, ?, ?)
    `).run(runId, 'Test Run', '{}');

    db.prepare(`
      INSERT INTO steps (id, run_id, sequence, type, label, tool_name, input, output, state_before, state_after)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(
      firstStepId,
      runId,
      1,
      'tool_call',
      'Read file',
      'read_file',
      JSON.stringify({ path: '/tmp/test.txt' }),
      JSON.stringify({ content: 'hello' }),
      JSON.stringify({ files: [] }),
      JSON.stringify({ files: ['/tmp/test.txt'] })
    );

    db.prepare(`
      INSERT INTO edges (run_id, source_step_id, target_step_id, relationship)
      VALUES (?, ?, ?, ?)
    `).run(runId, firstStepId, firstStepId, 'self');
  });

  after(() => {
    db.close();

    for (const suffix of ['', '-wal', '-shm']) {
      const filePath = `${testDbPath}${suffix}`;

      if (fs.existsSync(filePath)) {
        fs.unlinkSync(filePath);
      }
    }
  });

  it('GET /api/runs returns a list of runs', async () => {
    const res = await request(app).get('/api/runs').expect(200);

    assert.ok(Array.isArray(res.body.runs), 'runs should be an array');
    assert.strictEqual(res.body.runs.length, 1, 'should contain exactly one run');
    assert.strictEqual(res.body.runs[0].id, runId);
    assert.strictEqual(res.body.runs[0].name, 'Test Run');
  });

  it('GET /api/runs/:runId/graph returns nodes and edges', async () => {
    const res = await request(app).get(`/api/runs/${runId}/graph`).expect(200);

    assert.ok(res.body.run, 'should include run metadata');
    assert.strictEqual(res.body.run.id, runId);

    assert.ok(Array.isArray(res.body.nodes), 'nodes should be an array');
    assert.strictEqual(res.body.nodes.length, 1, 'should contain exactly one node');
    assert.strictEqual(res.body.nodes[0].id, firstStepId);
    assert.strictEqual(res.body.nodes[0].type, 'tool_call');

    assert.ok(Array.isArray(res.body.edges), 'edges should be an array');
    assert.strictEqual(res.body.edges.length, 1, 'should contain exactly one edge');
    assert.strictEqual(res.body.edges[0].sourceStepId, firstStepId);
    assert.strictEqual(res.body.edges[0].targetStepId, firstStepId);
  });

  it('GET /api/runs/:runId/graph returns 404 for missing run', async () => {
    const res = await request(app).get('/api/runs/nonexistent/graph').expect(404);

    assert.strictEqual(res.body.error, 'Run not found');
  });

  it('ingests a run and steps, then returns graph data for visualization', async () => {
    const createRunResponse = await request(app)
      .post('/api/runs')
      .send({
        id: integrationRunId,
        name: 'Integration Replay Run',
        metadata: { agent: 'integration-test' },
      });

    assert.strictEqual(createRunResponse.status, 201);

    const firstStepResponse = await request(app)
      .post(`/api/runs/${integrationRunId}/steps`)
      .send({
        id: integrationFirstStepId,
        type: 'tool_call',
        label: 'Read file',
        toolName: 'read_file',
        input: { path: 'README.md' },
        output: { ok: true },
        stateBefore: { files: 0 },
        stateAfter: { files: 1 },
      });

    assert.strictEqual(firstStepResponse.status, 201);

    const secondStepResponse = await request(app)
      .post(`/api/runs/${integrationRunId}/steps`)
      .send({
        id: integrationSecondStepId,
        type: 'state_change',
        label: 'Update state',
        sourceStepId: integrationFirstStepId,
        input: { reason: 'record file count' },
        output: { ok: true },
        stateBefore: { files: 1 },
        stateAfter: { files: 2 },
      });

    assert.strictEqual(secondStepResponse.status, 201);

    const listResponse = await request(app)
      .get('/api/runs')
      .expect(200);

    assert.ok(listResponse.body.runs.some((run) => run.id === integrationRunId));

    const graphResponse = await request(app)
      .get(`/api/runs/${integrationRunId}/graph`)
      .expect(200);

    assert.strictEqual(graphResponse.body.run.id, integrationRunId);
    assert.strictEqual(graphResponse.body.nodes.length, 2);
    assert.strictEqual(graphResponse.body.edges.length, 1);
    assert.strictEqual(graphResponse.body.edges[0].sourceStepId, integrationFirstStepId);
    assert.strictEqual(graphResponse.body.edges[0].targetStepId, integrationSecondStepId);
    assert.deepStrictEqual(graphResponse.body.nodes[1].stateBefore, { files: 1 });
    assert.deepStrictEqual(graphResponse.body.nodes[1].stateAfter, { files: 2 });
  });
});
