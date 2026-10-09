# REA 云端安装与实测记录

本目录是 `yhongzhi0707-dot/physics-html-demo` 中独立保存的 REA 配置，不改动教学页面。`setup.sh` 与 `start-skill.md` 保留了此前验证过的内容。

仓库包含配置、CLI/MCP 验收脚本、静态样本和 [验证摘要](verification-summary.json)。下面历史记录中的 `results/`、官方文档副本 `docs/` 及 `/workspace/rea-cloud` 路径属于原云端工作区；原始日志和文档副本没有提交。新的仓库工作区路径可能不同，运行时请从仓库根目录使用 `rea-cloud/` 相对路径。GitHub 保存不等于平台环境已发布。

从新的仓库工作区复用：环境 Install script 可使用 `bash rea-cloud/setup.sh`，前提是 setup 会话已经检出此配置所在分支或已合并的默认分支；否则粘贴脚本全文。Start skill 使用 `rea-cloud/start-skill.md` 内容。详细保存/发布步骤见 [PUBLISH.md](PUBLISH.md)。

验证日期：2026-10-09。当前云端已安装官方 `rea-agents@6.2.0`，可通过 CLI 做静态 JavaScript/Electron 分析，无需本地 Windows 电脑。

后续复用配置、安全审查、新 Codex 后端 MCP 实测及当前界面发布步骤见 [PUBLISH.md](PUBLISH.md)。该记录明确区分本机新进程测试与发布后的新云端任务测试。

## 官方依据与运行环境

- 仓库：<https://github.com/morluto/rea>
- 已阅读 [官方 README](https://github.com/morluto/rea/blob/5f16124a31fa4a82bd03037506809d6be959d768/README.md)、[安装文档](https://github.com/morluto/rea/blob/5f16124a31fa4a82bd03037506809d6be959d768/docs/installation.md)、CLI 与 JavaScript 工作流文档。本地副本在 `docs/`。
- 阅读时 main HEAD：`5f16124a31fa4a82bd03037506809d6be959d768`。
- npm 当时的最新版本为 `6.2.0`，并非安装文档发布记录段落提及的 `5.0.0`。实际 npm 元数据与安装结果保存在 `results/npm-package-metadata.json`、`results/npm-installed.json`。
- Debian 13 x86_64，Node.js `24.19.0`，npm `11.9.0`。
- 包要求 Node.js `^22.19.0 || ^24.11.0 || >=26.0.0`，当前版本符合。Node 23/25 不符合。
- 实际 CLI：`/home/agent/.local/bin/rea`。使用 npm 全局用户前缀；没有安装系统级分析引擎，没有修改现有代码项目。

## 已执行的安装步骤

```bash
npm install --global rea-agents@6.2.0 --no-audit --no-fund
rea --version
```

首次安装成功，npm 报告安装 142 个包。`rea --version` 返回 `6.2.0`。
可复用的 `setup.sh` 包含运行时检查、相同安装命令与安装后的版本校验；已在当前云端运行成功，也验证了重复执行。

后续已改进为：若检测到可运行的 REA 6.2.0，则跳过 npm 安装；同时确认 CLI 在 PATH 中。改进版本已运行验证，日志位于 `results/reuse-review/setup.stdout.log`。

```bash
bash /workspace/rea-cloud/setup.sh
```

脚本不执行 `rea setup`，不写代理配置，不安装 REA 技能或大型原生引擎。npm 下载依赖需要访问配置的 npm registry。

## 实际测试结果

| 测试 | 退出码 | 实际观察 | 原始记录 |
| --- | --- | --- | --- |
| 全局 `rea doctor --json` | 1 | Node 通过；Debian 原生主机检查不通过；Hopper/Ghidra/IDA 缺失；REA 技能与 Codex 注册缺失 | `results/doctor.json` |
| 目录静态 JavaScript 分析 | 0 | 7 个相关文件，5 个 JS 文件解析成功，0 个解析失败；32 个图节点、47 条边 | `results/javascript-directory.json` |
| ASAR 静态 JavaScript 分析 | 0 | 同一自建样本打包后的 ASAR 分析成功；39 个图节点、54 条边 | `results/javascript-asar.json` |
| IPC 功能追踪 | 0 | `search:query` 种子匹配 1 个节点，追踪图含 32 个节点、47 条边 | `results/javascript-trace.json` |
| MCP stdio 实测 | 0 | 服务版本 6.2.0；列出 139 个工具；实际分析调用返回完整 Evidence | `results/mcp-smoke.stdout.log`、`results/mcp-javascript.json` |
| 尝试 Ghidra 分析 `/usr/bin/true` | 1 | 返回 `provider_unavailable`；Ghidra 未配置 | `results/native-unavailable.json` |

目录与 ASAR 结果都验证了：`./utils.mjs` 的 ESM 导入、`./search.cjs` 的 CommonJS 导入、主进程/preload/contextBridge 关系，以及 1 组 `search:query` 发送端和主进程处理端配对。结果含源位置和静态证据。

样本在顶层放置了执行标记写入与抛错；分析后 `.executed` 文件不存在。所有分析读取样本而未运行它。未安装 Electron，也未进行 Electron 运行时测试。

功能追踪返回的是静态图关系，不证明这些代码在运行时可达。该追踪没有返回 terminal paths，不能把它描述为已验证的完整运行路径。其他真实应用、大型混淆包、source map 恢复等均未实测。

## Doctor 的失败与当前限制

`doctor` 的整体 `healthy=false` 已如实保留。Debian 13 不在其原生主机审计列出的发行版中，但静态 JavaScript CLI 和 stdio MCP 在本机实际测试成功。

- 深度原生反编译、原生调用关系等当前无法使用：Hopper/Ghidra/IDA 均未配置。
- 已有 Java 21 运行时，但没有 `javac`；未来使用 Ghidra 还需要符合版本要求的完整 JDK。
- macOS 原生 UI、签名、Swift/macOS 原生辅助工具等被能力检查标为 `unsupported_host`。
- Android/JADX、固件、浏览器、.NET、网络抓包与进程运行时功能没有实测；不将能力列表中出现的工具当成已验证可用。
- 没有安装 Hopper、Ghidra、IDA、JADX、浏览器或固件分析引擎。按你的要求，若后续要安装大型引擎，应先展示具体方案并征求批准。

## MCP 接入情况

REA 的官方 stdio 服务在云端可运行，协议级连接与分析已实测。`mcp-smoke.mjs` 使用 REA 自带的 MCP SDK，不需要额外安装 SDK。实际工具参数为 `input_path` 和 `format`，不是 CLI 位置参数 `path`。

首次 MCP 测试误用了 `path`，服务器拒绝该请求；相关记录保存在 `results/initial-*`。按服务实际 schema 改为 `input_path` 后复测成功。

当前 Codex 会话的工具目录没有 REA 工具。没有将协议测试描述为本次会话已完成 MCP 加载，也没有改动 `/run/codex-environment/codex-home/config.toml`。

已执行只读配置计划：

```bash
rea setup --client codex --skill=false --dry-run --json
```

计划见 `results/setup-plan.json`。本次通过 CLI 使用 REA。如果未来的 Codex 客户端支持加载自定义 stdio MCP，可参考 `mcp-config.example.toml`，配置后需重启/重新连接客户端；该模板没有应用到当前会话。

## 让 Codex 分析其他程序

把目标复制、下载或解压到云端可访问路径，然后给 Codex 明确目标和问题，例如：

> 使用 REA CLI 静态分析 `/workspace/targets/example-app`，追踪搜索功能的模块、IPC 和入口，报告证据与未知项，保存完整 JSON。不要运行目标程序。

目录或 ASAR 的已验证调用方式：

```bash
rea analyze-javascript-application /absolute/path/to/app --json > /absolute/path/to/application-evidence.json
rea analyze-javascript-application /absolute/path/to/app.asar --json > /absolute/path/to/asar-evidence.json
```

若全局 npm bin 不在 PATH：

```bash
bash /workspace/rea-cloud/rea-cli.sh analyze-javascript-application /absolute/path/to/app --json > /absolute/path/to/application-evidence.json
```

需要追踪功能时，将上一步完整 Evidence 放入输入 JSON 的 `application`，不要只截取 `normalized_result`：

```bash
python3 - /absolute/path/to/application-evidence.json /absolute/path/to/trace-input.json <<'PY'
import json, sys
with open(sys.argv[1], encoding='utf-8') as f:
    application = json.load(f)
with open(sys.argv[2], 'w', encoding='utf-8') as f:
    json.dump({
        'application': application,
        'seed': {'kind': 'channel', 'value': 'search:query'},
        'direction': 'both'
    }, f)
PY
```

然后运行 `rea trace-application-feature /absolute/path/to/trace-input.json --json`。已生成的实际输入例子是 `results/trace-input.json`。其他种子与参数须以 `rea --help`、官方工作流文档或真实 MCP schema 为准。

ELF/PE/原生可执行文件需要先配置合适的分析引擎；目前不能承诺用上面的 JavaScript 命令分析它们。

## 新任务复用的保存边界

已保存 `setup.sh`、`rea-cli.sh`、`environment-recipe.json`、MCP 模板、官方文档副本和原始测试输出。

**尚未保存到平台的云端环境启动配置。** 当前仅提供只读的 `cloud_environment.environment_status`；返回 `source_config_id=null`，且没有配置写入接口。因此不能声称新任务会自动安装，或当前容器的全局 npm 安装必然保留到新环境。

要在新任务中自动安装，请在你使用的云端环境设置中保存 `setup.sh` 的完整内容为环境安装脚本，并确认 Node.js 满足上述要求。若新任务没有这些工作区文件，需先保留并恢复脚本/归档；当前 `/workspace` 路径本身不是跨任务持久化保证。

最小安装命令是 `npm install --global rea-agents@6.2.0 --no-audit --no-fund`。平台配置保存和新任务启动尚未实测。
