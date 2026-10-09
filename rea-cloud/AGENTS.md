# REA cloud usage

The setup and verification report is README.md in this directory. The verified
version is rea-agents 6.2.0 on Debian 13, Node 24.19.0, npm 11.9.0.

When asked to analyze a supplied JavaScript/Electron directory or ASAR, use:

```bash
rea analyze-javascript-application /absolute/target/path --json
```

Save complete Evidence JSON for later workflows. rea-cli.sh resolves the global
npm executable if PATH does not expose rea. If REA is absent, setup.sh installs
the tested official version without external analysis engines or agent changes.

Use CLI when no REA MCP tools are present in the active session. A successful
standalone stdio test does not prove the active agent loaded REA.

Do not claim doctor passes globally: its audited exit code is 1. Native engines
are not installed. Ask the user before installing large analysis engines or
modifying an existing project, as requested in this task. Keep untested features
separate from successful tests, and do not execute analysis targets merely to
perform static analysis.

The local setup recipe is saved, but platform startup configuration was not
written: the available cloud configuration interface is read-only.

The reusable-environment handoff is PUBLISH.md. setup.sh now skips npm install
when the exact tested REA version already runs and fails if the npm bin directory
is not on PATH. start-skill.md is prepared for the cloud environment Start skill
field. Neither field has been saved through the platform API.

A new Codex app-server thread connected to REA and called its JavaScript tool
successfully. That test used process-level configuration and no model API turn;
codex exec's model turn failed with HTTP 401. No new cloud VM or published
environment has been tested. Preserve these distinctions in reports.
