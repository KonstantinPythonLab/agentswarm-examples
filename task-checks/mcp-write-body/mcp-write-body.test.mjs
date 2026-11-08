import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { test } from 'node:test';

assert.ok(process.env.BOUNTY_REPO, 'Set BOUNTY_REPO to your agentswarm-mcp branch checkout');
const { createApi } = await import(pathToFileURL(path.join(path.resolve(process.env.BOUNTY_REPO), 'server/api.js')));

for (const tool of ['deliver_result', 'ask_question']) {
  for (const body of ['', ' ', '\t\t', '\r\n', ' \t\n ', '\u00a0', '\u3000']) {
    test(`${tool} rejects blank body ${JSON.stringify(body)} before identity or post requests`, async () => {
      const original = globalThis.fetch;
      const calls = [];
      globalThis.fetch = async (url, options) => {
        calls.push({ url: String(url), method: options.method });
        if (new URL(url).pathname === '/api/me') return Response.json({ member: { handle: 'fixture_agent' } });
        return Response.json({ error: 'Body must contain text' }, { status: 400 });
      };
      try {
        const api = createApi({ AGENTSWARM_BASE_URL: 'http://127.0.0.1:1', AGENTSWARM_API_KEY: 'dummy-fixture-key', AGENTSWARM_HANDLE: 'fixture_agent' });
        await assert.rejects(api.call(tool, { parentId: `post_${randomUUID()}`, body }), 'Blank bodies must be rejected locally');
        assert.deepEqual(calls, [], 'Reject whitespace-only bodies before any identity or post HTTP request');
      } finally { globalThis.fetch = original; }
    });
  }
  test(`${tool} preserves a nonblank body and identity/write behavior`, async () => {
    const original = globalThis.fetch;
    const calls = [];
    const parentId = `post_${randomUUID()}`;
    const resultId = `result_${randomUUID()}`;
    const requestId = randomUUID();
    const body = `  Entrega útil ${randomUUID()}\n第二行\t `;
    globalThis.fetch = async (url, options) => {
      const pathname = new URL(url).pathname;
      calls.push({ pathname, options });
      if (pathname === '/api/me') return Response.json({ member: { handle: 'fixture_agent' } });
      assert.equal(pathname, '/api/posts');
      assert.equal(options.method, 'POST');
      assert.deepEqual(JSON.parse(options.body), { parentId, body, requestId, ...(tool === 'deliver_result' ? { type: 'result' } : {}) });
      return Response.json({ post: { id: resultId } });
    };
    try {
      const api = createApi({ AGENTSWARM_BASE_URL: 'http://127.0.0.1:1', AGENTSWARM_API_KEY: 'dummy-fixture-key', AGENTSWARM_HANDLE: 'fixture_agent' });
      const result = await api.call(tool, { parentId, body, requestId });
      assert.equal(result.id, resultId);
      assert.equal(result.requestId, requestId);
      assert.equal(result.verifiedHandle, 'fixture_agent');
      assert.deepEqual(calls.map(call => [call.pathname, call.options.method]), [['/api/me', 'GET'], ['/api/posts', 'POST']]);
      assert.ok(calls.every(call => call.options.headers.Authorization === 'Bearer dummy-fixture-key'));
    } finally { globalThis.fetch = original; }
  });
}
