"""Run both CLI binaries against a loopback-only task-feed fixture."""
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

import pytest

assert os.environ.get('BOUNTY_REPO'), 'Set BOUNTY_REPO to your agentswarm-cli branch checkout.'
REPO = Path(os.environ['BOUNTY_REPO']).resolve()
assert (REPO / 'node/bin/agentswarm.js').is_file(), 'BOUNTY_REPO must contain node/bin/agentswarm.js'

@pytest.mark.parametrize('language', ['node', 'python'])
@pytest.mark.parametrize('flag,expected_code', [('--task', 0), ('--mission', 2)])
def test_tasks_parent_filter_uses_current_api(language, flag, expected_code, tmp_path):
    calls = []
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass
        def do_GET(self):
            parsed = urlsplit(self.path)
            calls.append((parsed.path, parse_qs(parsed.query)))
            payload = json.dumps({'items': [], 'nextCursor': None}).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, kwargs={'poll_interval': 0.01}, daemon=True)
    thread.start()
    try:
        env = dict(os.environ, AGENTSWARM_BASE_URL=f'http://127.0.0.1:{server.server_port}', AGENTSWARM_API_KEY='', AGENTSWARM_CONFIG_DIR=str(tmp_path), PYTHONPATH=str(REPO / 'python/src'))
        command = ['node', str(REPO / 'node/bin/agentswarm.js')] if language == 'node' else [sys.executable, '-m', 'agentswarm_cli']
        result = subprocess.run(command + ['tasks', flag, 'post_parent', '--json'], env=env, capture_output=True, text=True, timeout=5)
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
    assert result.returncode == expected_code, f'{language} {flag}: exit {result.returncode}; stderr: {result.stderr}'
    if flag == '--task':
        assert calls == [('/api/feed', {'type': ['task'], 'task': ['post_parent']})]
        assert json.loads(result.stdout)['items'] == []
    else:
        assert calls == [], 'Retired --mission must fail locally before HTTP'

@pytest.mark.parametrize('language', ['node', 'python'])
def test_tasks_help_names_parent_filter(language, tmp_path):
    env = dict(os.environ, AGENTSWARM_API_KEY='', AGENTSWARM_CONFIG_DIR=str(tmp_path), PYTHONPATH=str(REPO / 'python/src'))
    command = ['node', str(REPO / 'node/bin/agentswarm.js')] if language == 'node' else [sys.executable, '-m', 'agentswarm_cli']
    result = subprocess.run(command + ['--help'], env=env, capture_output=True, text=True, timeout=5)
    assert result.returncode == 0
    task_help = result.stdout.split('  tasks ', 1)[1].split('  read ', 1)[0]
    assert '--task' in task_help and '--mission' not in task_help
