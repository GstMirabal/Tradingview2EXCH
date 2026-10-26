# Upstream Findings for the `.agents` Framework

Framework-class defects found while working in this host (`agents.md §4
feedback_upstream`). `§3 strict_rule` forbids patching them inside the submodule;
each is drafted here, genericized under `RA-15`, for submission as an issue or PR
to the `.agents` repository from a separate clone.

| ID | Found in | Pinned version | Status |
| :--- | :--- | :--- | :--- |
| KI-004-3 | Sprint #004 | `v4.39.1` | Drafted, not submitted |
| KI-004-5 | Sprint #004 | `v4.39.1` | Drafted, not submitted |

---

## KI-004-3 — The `graphify` MCP server is registered but its runtime is never installed

**Observed.** At every session start in a host, Claude Code reports the `graphify`
MCP server as `CONNECTION_CLOSED`. Running the registered command by hand:

```
.agents/venv_skillopt/bin/python -I -m graphify.serve graphify-out/graph.json
ModuleNotFoundError: No module named 'mcp'
```

**Cause.** `claude/mcp.json` registers the server, and `install_claude.sh` merges it
into the host's `.mcp.json`, but `requirements-core.txt` (with
`requirements-quality.txt`) installs `graphifyy` without the `mcp` package that
`graphify/serve.py` imports.

**Proposed fix.** Pin the MCP runtime in `requirements-core.txt` (the `graphifyy`
MCP extra if one exists, otherwise `mcp` at an exact version), plus a test that
imports `graphify.serve` from the core environment.

---

## KI-004-5 — `model_ledger.py` writes into the submodule when run from a host

**Observed.** `close_workflow.md` Phase 1 `model_ledger_regen` tells a host to run
`make model-ledger`. That target runs `cd $(AGENTS_DIR) && python3 scripts/model_ledger.py`,
and the script writes to `agents_root() / "docs/audits/MODEL_LEDGER.md"`. In a host,
`agents_root()` is the `.agents/` submodule checkout.

**Consequence.** Following the step as written dirties the submodule, which violates
`agents.md §3 strict_rule` and makes Phase 5 `submodule_purity` exit `2`. The same
close therefore cannot pass both steps.

**Proposed fix.** Resolve the output and the sprint directories it reads from the
host root in host mode, the same split `_root.py` already documents as "Mixed" for
`branch_sovereignty`. Alternatively, mark the step nucleus-only in
`close_workflow.md`.
