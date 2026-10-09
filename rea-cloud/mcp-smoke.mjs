import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';
import { writeFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = dirname(fileURLToPath(import.meta.url));
const npmRoot = execFileSync('npm', ['root', '--global'], { encoding: 'utf8' }).trim();
const require = createRequire(join(npmRoot, 'rea-agents', 'package.json'));
const { Client } = require('@modelcontextprotocol/client');
const { StdioClientTransport } = require('@modelcontextprotocol/client/stdio');
const reaCommand = process.env.REA_CLI_PATH || 'rea';
const transport = new StdioClientTransport({
  command: reaCommand,
  args: ['mcp'],
  cwd: root,
  env: { ...process.env },
  stderr: 'pipe'
});
let stderr = '';
transport.stderr?.on('data', (chunk) => { stderr += chunk.toString(); });
const client = new Client({ name: 'rea-cloud-smoke', version: '1.0.0' }, { capabilities: {} });

try {
  await client.connect(transport, { timeout: 30000 });
  const tools = [];
  let cursor;
  do {
    const page = await client.listTools(cursor ? { cursor } : undefined);
    tools.push(...page.tools);
    cursor = page.nextCursor;
  } while (cursor);
  writeFileSync(join(root, 'results', 'mcp-tools.json'), JSON.stringify(tools, null, 2));
  const analysisTool = tools.find((tool) => tool.name === 'analyze_javascript_application');
  if (!analysisTool) throw new Error('Server did not advertise analyze_javascript_application');
  console.log(JSON.stringify({
    server: client.getServerVersion(),
    tool_count: tools.length,
    analysis_tool: analysisTool.name,
    input_schema: analysisTool.inputSchema
  }));
  const result = await client.callTool({
    name: analysisTool.name,
    arguments: { input_path: join(root, 'fixtures', 'electron-demo'), format: 'directory' }
  }, { timeout: 90000 });
  writeFileSync(join(root, 'results', 'mcp-javascript.json'), JSON.stringify(result, null, 2));
  if (result.isError) throw new Error('MCP analysis returned isError; inspect results/mcp-javascript.json');
  console.log(JSON.stringify({ call_succeeded: true, result_keys: Object.keys(result) }));
} finally {
  await client.close();
  writeFileSync(join(root, 'results', 'mcp-server.stderr.log'), stderr);
}
