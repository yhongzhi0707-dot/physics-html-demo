# 将 REA 保存为可复用 Codex Cloud 环境

## 从本仓库复用配置

本目录仅保存 REA 配置、静态样本和验收工具。GitHub 中的文件或 PR 不会自动保存/发布 Codex Cloud 环境。

审核并手动合并配置 PR 后，在新环境中选择 `yhongzhi0707-dot/physics-html-demo`，确认 setup 会话已经检出含有 `rea-cloud/` 的提交。环境 **Install script** 可填写 `bash rea-cloud/setup.sh`，或直接粘贴 `setup.sh` 全文；**Start skill** 填写 `start-skill.md` 内容。若尚未合并且界面支持选择分支，可以使用配置 PR 分支。

新的检出路径不必是 `/workspace/rea-cloud`。从仓库根目录验收静态样本时使用 `rea analyze-javascript-application "$PWD/rea-cloud/fixtures/electron-demo" --json`。输出保存到 `/tmp` 或本目录被忽略的 `results/`，不要写入教学页面。

下面提到的原始 `results/` 日志仍留在最初的云端工作区，不纳入仓库。仓库里的 `verification-summary.json` 仅保留此前测试的非敏感统计和边界；本次保存配置不执行安装、不再次启动分析目标或发布环境。

本次已经审查和改进安装脚本，并验证新 shell 的 CLI 和新 Codex app-server 会话的 MCP。**平台环境配置没有保存或发布，也没有启动新的云端 VM。** 当前可用接口只有只读环境状态；`source_config_id=null`，没有环境创建、编辑或发布接口。

## 脚本与依赖审查

- `setup.sh` 以 `set -euo pipefail` 处理失败，校验 Node 支持范围并固定 `rea-agents@6.2.0`。
- 已有可运行的 `6.2.0` 时跳过 npm 安装；本次执行日志确认走了跳过分支，没有重复安装组件。
- 安装后检查精确版本，并检查全局 npm bin 是否在 PATH。若 PATH 不满足要求，脚本明确失败，避免把 setup 子 shell 的临时 export 当成后续任务的配置。
- 没有 curl 管道运行远端脚本、TLS 校验关闭、sudo、凭据读取、登录操作或原生引擎安装。
- 包内 32 个直接依赖都使用精确版本，逐项读取实际安装的包版本，32/32 与声明一致；npm 固定版本的发布 integrity 与上一轮保存的值一致。传递依赖不是完全锁定的安装快照；本次没有执行依赖漏洞审计，不能宣称无漏洞。
- MCP 模板改为直接启动已安装的 REA，避免新会话再通过 npx 下载一份包。路径需与目标环境的实际 npm 前缀一致。

## 本次新增实测

| 测试 | 结果 | 边界 |
| --- | --- | --- |
| 改进后的 `setup.sh` | 成功；检测到 6.2.0 并跳过安装；CLI 在 PATH | 当前容器 |
| 新 Bash 进程静态 JS 分析 | 成功；5 个 JS 文件，0 个解析失败，1 组 IPC 配对 | 当前容器的新进程，不是新 VM |
| 新 Codex app-server 会话 MCP | `connected`；139 个工具；真实分析调用成功并返回完整 Evidence | 使用进程级 MCP 配置，不修改平台托管会话 |
| 新 `codex exec` 模型回合 | 失败，退出 1；模型 API 401，认证无法刷新 | MCP 服务和本机静态分析不依赖这个模型请求 |
| 平台新环境发布与新任务验收 | 未完成 | 没有环境编辑/发布工具，需要界面操作 |

日志在 `results/reuse-review/`。MCP 成功记录是 `codex-app-server.summary.json`、`codex-mcp-status.json`、`codex-mcp-javascript.json`。新 shell 记录是 `new-shell.status.json`、`new-shell-javascript.json`。模型认证失败记录是 `new-codex.status.json`、`new-codex.stderr.log`。

## 需要你在界面上完成的操作

以下字段和流程依据当前 [官方 Codex Cloud 环境指南](https://developers.openai.com/codex/environments/cloud-environments)，不是旧版 setup/maintenance-script 界面。

1. 打开 **Settings → Codex Cloud → Environments**。已有适合的环境时，在其 **… → Edit** 中修改；没有时选择 **Create environment**。也可以从新任务 **Work in → Cloud → Select environment → Create environment** 进入。
2. 若创建流程要求仓库，选择你实际要工作的仓库，并按需完成 GitHub 连接。使用 REA npm CLI 不要求克隆或源码构建 `morluto/rea`；不要因此安装整个 REA 开发工具链。
3. 将 `setup.sh` 的**完整内容**纳入环境 **Install script**。不要只填写当前 `/workspace/rea-cloud/setup.sh` 路径，除非设置流程已把该文件放进准备发布的环境中。setup 会话中明确要求保留兼容 Node 版本并只安装固定的 REA CLI。
4. 将 `start-skill.md` 的内容纳入 **Start skill**。如果界面通过 setup 对话来编辑这两个字段，可以直接发送下面的设置请求并附上/粘贴文件内容。
5. 安装阶段允许访问 npm：在网络设置中使用 **Package managers** 预设，或只允许 `registry.npmjs.org`。本地静态 JS 分析和本地 MCP 不需要额外放开任意互联网域名。不要修改代理或 CA 设置。
6. 在 setup 会话中验证 `rea --version` 返回 `6.2.0`，且 `command -v rea` 成功。当前安装路径是 `/home/agent/.local/bin/rea`；新环境若前缀不同，以 `npm prefix --global` 为准。如果 PATH 不包含该前缀的 `bin` 目录，在 **Environment variables → Manage** 中把这个目录加入 PATH 并保留原路径内容，再验证。不要把未展开的 `$PATH` 字面值保存进去。
7. 如需 MCP，让支持自定义 stdio MCP 的 Codex 客户端保存 `mcp-config.example.toml` 中的表，检查可执行文件路径，并在新会话查看 REA 是否实际加载。官方 `rea setup --client codex --skill=false --dry-run --json` 可先给出具体计划；确认仅注册 Codex、没有引擎安装后再应用该范围。平台托管会话若不加载本地客户端配置，使用 CLI；发布文件系统本身不能保证托管会话 MCP 工具注册。
8. 查看 setup 报告和配置，选择 **Save draft**（或界面的保存操作），再选择 **Publish**；更新已有环境时选择 **Republish**。新任务使用发布后的文件系统；仅在当前任务里安装或保存草稿不足以证明新任务会继承。
9. 出现 **Environment published** 后，选择 **Start a new task**，确认所选是刚发布的环境，并发送下方验收请求。新任务结果应另行记录；本报告不能代替该测试。

可在环境设置对话中发送：

> 将附上的 setup.sh 完整内容保存到 Install script，将 start-skill.md 内容保存到 Start skill。固定使用 rea-agents@6.2.0；兼容的 Node/npm 保持现状，已有正确 REA 版本时跳过安装。不安装 Ghidra、Hopper 或额外分析引擎。验证 CLI、检查 PATH，保留静态分析测试输出，并给出可发布的设置报告。请不要把当前任务文件的保存当作环境已发布。

## 新任务验收请求

> 验证发布环境中的 REA：不要重新安装依赖。执行 node --version、npm --version、command -v rea、rea --version。创建带本地 import/require 的小型 JavaScript 样本，仅做静态分析，读取完整 JSON，报告解析成功与失败数。检查当前会话是否实际加载 REA MCP；若没有，通过 CLI 分析并报告 MCP 未加载。不要安装 Ghidra/Hopper，也不要执行目标程序。

若本目录及样本已经随准备好的文件系统发布，也可直接调用：

```bash
rea analyze-javascript-application /workspace/rea-cloud/fixtures/electron-demo --json > /tmp/rea-new-task-evidence.json
```

读取 Evidence 中的 `normalized_result.statistics` 和 `normalized_result.summary.ipc`，不能只用退出码宣称所有关系正确。样本执行标记 `.executed` 应保持不存在。

## 仍需人工或平台配置的事项

- 保存/发布环境，以及发布后开启新任务验收：本次没有编辑接口可执行。
- 托管新会话是否载入本地 MCP 配置：需要平台支持和新任务实际工具列表来确认；当前 CLI 后端的成功不能替代它。
- 若使用独立 `codex exec` 让模型调用 MCP，需要该客户端可用的认证上下文；本次返回 401，没有执行登录或更改凭据。
- 原生反编译仍未配置；按照你的要求没有安装 Ghidra/Hopper。
