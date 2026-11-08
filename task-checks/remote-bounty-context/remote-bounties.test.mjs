import test from 'node:test';
import assert from 'node:assert/strict';
import { resolve } from 'node:path';
import { existsSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

assert.ok(process.env.BOUNTY_REPO, 'Set BOUNTY_REPO to your agentswarm-remote branch checkout.');
const repo = resolve(process.env.BOUNTY_REPO);
assert.ok(existsSync(resolve(repo, 'src/index.js')), 'BOUNTY_REPO must contain src/index.js');
const fixtures = [
  { id: 'post_step', title: 'Step bounty', status: 'open', underTaskId: 'post_parent', funders: 2, paidBy: 'shared', bounty: { reward: '$10', sourceUrl: null } },
  { id: 'post_root', title: 'Root bounty', status: 'open', underTaskId: null, funders: null, paidBy: 'escrow', bounty: { reward: '$10', amountUsd: 10 } },
];
for (const row of fixtures) {
  test(`list_bounties preserves parent task and funder count for ${row.id}`, async t => {
    const originalFetch = globalThis.fetch;
    const originalCaches = globalThis.caches;
    t.after(() => { globalThis.fetch = originalFetch; globalThis.caches = originalCaches; });
    let calls = 0;
    let writes = 0;
    let hits = 0;
    const stored = new Map();
    globalThis.caches = { default: {
      async match(key) {
        const response = stored.get(key.url);
        if (response) hits++;
        return response?.clone();
      },
      async put(key, response) {
        writes++;
        stored.set(key.url, response.clone());
      },
    } };
    globalThis.fetch = async (url, options) => {
      assert.equal(url, 'https://agentswarm.space/api/bounties');
      assert.equal(options.method, 'GET');
      calls++;
      return Response.json({ bounties: [row], nextCursor: null });
    };
    const moduleUrl = pathToFileURL(resolve(repo, 'src/index.js')).href;
    const worker = (await import(`${moduleUrl}?fixture=${row.id}-miss`)).default;
    const request = () => new Request('https://fixture.invalid/mcp', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ jsonrpc: '2.0', id: 1, method: 'tools/call', params: { name: 'list_bounties', arguments: {} } }),
    });
    const envelope = await (await worker.fetch(request())).json();
    assert.equal(envelope.result.isError, false);
    const expected = { underTaskId: row.underTaskId, funders: row.funders };
    const fields = actual => ({ underTaskId: actual.underTaskId, funders: actual.funders });
    const actual = envelope.result.structuredContent.data.bounties[0];
    assert.deepEqual(fields(actual), expected, 'Live projection must retain parent task and funder count');
    assert.equal(calls, 1);
    assert.equal(actual.paidBy, row.paidBy);
    assert.equal(writes, 1, 'Expected one Cache API write');
    const saved = await stored.get('https://agentswarm.space/api/bounties').clone().json();
    assert.deepEqual(fields(saved.result.bounties[0]), expected, 'Stored cache projection must retain parent task and funder count');
    // A fresh module has an empty isolate cache, so the next request must read the Cache API.
    const cachedWorker = (await import(`${moduleUrl}?fixture=${row.id}-hit`)).default;
    const cachedEnvelope = await (await cachedWorker.fetch(request())).json();
    assert.equal(cachedEnvelope.result.isError, false);
    const cached = cachedEnvelope.result.structuredContent.data.bounties[0];
    assert.deepEqual(fields(cached), expected, 'Cache-hit response must retain parent task and funder count');
    assert.equal(cached.paidBy, row.paidBy);
    assert.equal(hits, 1, 'Later request must hit the stored Cache API response');
    assert.equal(calls, 1, 'Cache hit must not fetch upstream again');
    assert.equal(writes, 1, 'Cache hit must not rewrite the projection');
  });
}
