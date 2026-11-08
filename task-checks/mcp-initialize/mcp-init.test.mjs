import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { resolve } from 'node:path';
import { existsSync } from 'node:fs';

assert.ok(process.env.BOUNTY_REPO, 'Set BOUNTY_REPO to your agentswarm-mcp branch checkout.');
const repo = resolve(process.env.BOUNTY_REPO);
assert.ok(existsSync(resolve(repo, 'server/index.js')), 'BOUNTY_REPO must contain server/index.js');
// server/index.js at agentswarm-mcp 78c88ff1d36b61aaf01a111cb3a6608394a5844e
// declares these four supported versions; keep negotiation coverage independent of the branch.
const supportedVersions = ['2024-11-05', '2025-03-26', '2025-06-18', '2025-11-25'];
const valid = { protocolVersion: '2025-06-18', capabilities: {}, clientInfo: { name: 'fixture', version: '1' } };
function initialize(params) {
  const input = [{ jsonrpc: '2.0', id: 1, method: 'initialize', params }, { jsonrpc: '2.0', id: 2, method: 'ping' }].map(JSON.stringify).join('\n') + '\n';
  const child = spawnSync(process.execPath, [resolve(repo, 'server/index.js')], {
    input, encoding: 'utf8', timeout: 5000,
    env: { ...process.env, AGENTSWARM_BASE_URL: 'http://127.0.0.1:1', AGENTSWARM_API_KEY: '', AGENTSWARM_HANDLE: '' },
  });
  assert.equal(child.status, 0, child.stderr || String(child.error));
  assert.equal(child.stderr, '');
  const replies = child.stdout.trim().split('\n').map(JSON.parse);
  assert.equal(replies.length, 2);
  assert.deepEqual(replies[1], { jsonrpc: '2.0', id: 2, result: {} });
  return replies[0];
}
for (const value of [null, [], 'bad', 42, false]) {
  test(`initialize rejects malformed capabilities ${JSON.stringify(value)}`, () => {
    const reply = initialize({ ...valid, capabilities: value });
    assert.equal(reply.error?.code, -32602, `expected -32602; got ${JSON.stringify(reply)}`);
    assert.equal(Object.hasOwn(reply, 'result'), false);
  });
}
for (const value of [null, [], 'bad', 42, false, {}, { name: 'fixture' }, { name: 7, version: '1' }, { name: 'fixture', version: null }]) {
  test(`initialize rejects malformed clientInfo ${JSON.stringify(value)}`, () => {
    const reply = initialize({ ...valid, clientInfo: value });
    assert.equal(reply.error?.code, -32602, `expected -32602; got ${JSON.stringify(reply)}`);
    assert.equal(Object.hasOwn(reply, 'result'), false);
  });
}
for (const protocolVersion of supportedVersions) {
  test(`initialize negotiates supported version ${protocolVersion}`, () => {
    assert.equal(initialize({ ...valid, protocolVersion }).result?.protocolVersion, protocolVersion);
  });
}
test('initialize retains valid metadata, omitted metadata and unknown-version fallback', () => {
  for (const params of [valid, { protocolVersion: '2025-06-18' }, { ...valid, protocolVersion: 'unknown' }]) {
    assert.equal(initialize(params).result.protocolVersion, '2025-06-18');
  }
});
