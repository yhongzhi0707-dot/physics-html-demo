# REA 环境启动与使用

此内容用于 Codex Cloud 环境的 **Start skill** 字段。

1. 启动任务时执行 `node --version`、`npm --version`、`rea --version`，确认 REA 为 `6.2.0`，Node 符合 `^22.19.0 || ^24.11.0 || >=26.0.0`。不要在每个任务启动时重复安装依赖。
2. 若 `rea` 不在 PATH，检查 `npm prefix --global` 返回目录中的 `bin/rea`。使用该绝对路径临时调用，并报告环境 PATH 需修复。若包不存在或版本错误，报告安装配置需修复，不要悄悄升级或安装其他分析引擎。
3. CLI 为默认调用方式，不需要常驻服务。静态分析命令：`rea analyze-javascript-application /absolute/path/to/app --json`；支持 JavaScript/Electron 目录和 ASAR。保存完整 Evidence JSON 供后续追踪使用。
4. 优先检查当前会话是否实际提供 REA MCP 工具；若没有，继续用 CLI。仅写入客户端 MCP 配置或完成独立协议测试，不能视为平台托管会话已经加载 MCP。
5. 有本地 Codex 客户端加载 MCP 时，启动已安装的 REA：`/home/agent/.local/bin/rea mcp`。以当前真实安装路径和服务 schema 为准，分析工具参数是 `input_path`、`format`。若全局前缀不同，调整命令路径。
6. 需要验收新任务时，创建只有本地 import/require 的小型 JS 样本，运行静态分析并读取真实 Evidence；不要执行目标程序。报告解析结果和未知项。
7. `rea doctor` 的全局审计可能因 Debian 原生主机检查、原生引擎和客户端注册缺失而退出 1；应读取失败原因，不能将它误报为通过或直接断言静态 JS 不可用。
8. 不安装 Ghidra、Hopper、IDA、JADX 或其他额外分析引擎；不运行被分析目标，除非用户明确要求并授权运行时观察。
