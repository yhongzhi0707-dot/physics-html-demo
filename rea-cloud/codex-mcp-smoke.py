#!/usr/bin/env python3
"""Test a new Codex app-server thread's REA MCP without a model API turn."""
import json
import os
from pathlib import Path
import queue
import signal
import subprocess
import threading
import time

root = Path(__file__).resolve().parent
out = root / 'results' / 'reuse-review'
out.mkdir(parents=True, exist_ok=True)
prefix = subprocess.check_output(['npm', 'prefix', '--global'], text=True).strip()
rea = str(Path(prefix) / 'bin' / 'rea')
args = [
    'codex', 'app-server', '--stdio',
    '-c', 'mcp_servers.rea.command=' + json.dumps(rea),
    '-c', 'mcp_servers.rea.args=["mcp"]',
    '-c', 'mcp_servers.rea.startup_timeout_sec=30'
]
messages = queue.Queue()
events = []
next_id = 0
summary = {'new_codex_process': True, 'new_cloud_environment': False,
           'model_turn_started': False, 'mcp_analysis_success': False}

with (out / 'codex-app-server.stderr.log').open('w') as stderr:
    proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=stderr, text=True, bufsize=1, start_new_session=True)

    def read_stdout():
        for line in proc.stdout:
            try:
                value = json.loads(line)
                events.append(value)
                messages.put(value)
            except ValueError:
                pass
        messages.put(None)

    reader = threading.Thread(target=read_stdout, daemon=True)
    reader.start()

    def send(value):
        proc.stdin.write(json.dumps(value) + '\n')
        proc.stdin.flush()

    def rpc(method, params, timeout=45):
        global next_id
        next_id += 1
        current = next_id
        send({'id': current, 'method': method, 'params': params})
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(f'Codex method {method} timed out')
            value = messages.get(timeout=remaining)
            if value is None:
                raise RuntimeError(f'Codex exited before {method} completed')
            if value.get('id') != current:
                continue
            if 'error' in value:
                raise RuntimeError(f'{method}: {json.dumps(value["error"])}')
            return value['result']

    try:
        rpc('initialize', {'clientInfo': {'name': 'rea-cloud-verifier', 'version': '1.0.0'},
                           'capabilities': {'experimentalApi': True}})
        send({'method': 'initialized', 'params': {}})
        thread = rpc('thread/start', {'cwd': str(root), 'ephemeral': True,
                                      'approvalPolicy': 'never', 'sandbox': 'read-only'})
        thread_id = thread['thread']['id']
        summary['thread_id'] = thread_id
        catalog = rpc('mcpServerStatus/list', {'threadId': thread_id, 'limit': 100})
        (out / 'codex-mcp-status.json').write_text(json.dumps(catalog, indent=2) + '\n')
        rea_status = next(item for item in catalog['data'] if item['name'] == 'rea')
        summary.update({'runtime_status': rea_status.get('runtimeStatus'),
                        'tool_count': len(rea_status['tools']),
                        'tools_error': rea_status.get('toolsError'),
                        'server_info': rea_status.get('serverInfo')})
        if not any(tool['name'] == 'analyze_javascript_application'
                   for tool in rea_status['tools'].values()):
            raise RuntimeError('New Codex thread did not discover REA analysis tool')
        result = rpc('mcpServer/tool/call', {
            'threadId': thread_id, 'server': 'rea',
            'tool': 'analyze_javascript_application',
            'arguments': {'input_path': str(root / 'fixtures' / 'electron-demo'),
                          'format': 'directory'}
        }, timeout=90)
        (out / 'codex-mcp-javascript.json').write_text(json.dumps(result, indent=2) + '\n')
        if result.get('isError'):
            raise RuntimeError('REA tool returned isError')
        evidence = result['structuredContent']
        normalized = evidence['normalized_result']
        assert evidence['operation'] == 'analyze_javascript_application'
        assert normalized['statistics']['parsed_javascript_files'] == 5
        assert normalized['statistics']['parse_failures'] == 0
        assert normalized['summary']['ipc']['paired_renderer_transmissions'] == 1
        assert not (root / 'fixtures' / 'electron-demo' / '.executed').exists()
        summary.update({'mcp_analysis_success': True, 'evidence_id': evidence['evidence_id'],
                        'statistics': normalized['statistics'], 'ipc': normalized['summary']['ipc']})
    except Exception as exc:
        summary['failure'] = f'{type(exc).__name__}: {exc}'
        raise
    finally:
        proc.stdin.close()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
        reader.join(timeout=2)
        (out / 'codex-app-server.events.jsonl').write_text(
            ''.join(json.dumps(item) + '\n' for item in events))
        (out / 'codex-app-server.summary.json').write_text(json.dumps(summary, indent=2) + '\n')
        print(json.dumps(summary, ensure_ascii=False))
