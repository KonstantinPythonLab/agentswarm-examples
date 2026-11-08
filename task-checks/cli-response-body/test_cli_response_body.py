"""Black-box CLI checks: dropped HTTP bodies must be network errors (exit 7)."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
from threading import Thread
from uuid import uuid4

import pytest

assert os.environ.get('BOUNTY_REPO'), 'Set BOUNTY_REPO to your agentswarm-cli branch checkout'
REPO = Path(os.environ['BOUNTY_REPO']).resolve()


@pytest.mark.parametrize('language', ['node', 'python'])
@pytest.mark.parametrize('mode,expected', [('truncated', 7), ('healthy', 0), ('http503', 6)])
def test_cli_response_body_network_error(language, mode, expected, tmp_path):
    handle = 'fixture_' + uuid4().hex[:12]
    seen = []

    class Handler(BaseHTTPRequestHandler):
        protocol_version = 'HTTP/1.1'

        def do_GET(self):
            seen.append((self.path, self.headers.get('Authorization')))
            data = json.dumps({'member': {'handle': handle}}).encode()
            status = 503 if mode == 'http503' else 200
            if mode == 'http503':
                data = b'{"error":"fixture unavailable"}'
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data) + 37 if mode == 'truncated' else len(data)))
            self.send_header('Connection', 'close')
            self.end_headers()
            self.wfile.write(data)
            self.wfile.flush()
            self.close_connection = True

        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        env = {'PATH': os.environ['PATH'], 'AGENTSWARM_CONFIG_DIR': str(tmp_path),
               'AGENTSWARM_BASE_URL': f'http://127.0.0.1:{server.server_port}',
               'AGENTSWARM_API_KEY': 'dummy-local-fixture-key',
               'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONPATH': str(REPO / 'python/src')}
        command = ['node', str(REPO / 'node/bin/agentswarm.js')] if language == 'node' else [sys.executable, '-m', 'agentswarm_cli']
        result = subprocess.run([*command, 'whoami', '--json'], env=env, capture_output=True, text=True, timeout=10)
        assert result.returncode == expected, (
            f'{language} {mode}: expected exit {expected}, got {result.returncode}; '
            f'an interrupted response body is a network error, not a generic error/success. stderr: {result.stderr}')
        assert seen == [('/api/me', 'Bearer dummy-local-fixture-key')], 'Do not automatically retry or change the request'
        if mode == 'truncated':
            assert result.stdout == '', 'Do not print a partial response as successful JSON'
            assert result.stderr.strip(), 'Print a useful network error'
            assert 'Traceback' not in result.stderr and 'UnhandledPromiseRejection' not in result.stderr
        elif mode == 'healthy':
            assert json.loads(result.stdout)['member']['handle'] == handle
            assert result.stderr == ''
        else:
            assert json.loads(result.stdout)['error'] == 'fixture unavailable'
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
