# Task Brief: `ap-multitool` Monorepo Consolidation Sprint

**Branch:** `refactor/ap-multitool-monorepo-consolidation`  
**Monorepo Target:** `Z:\repos\ap-multitool`  
**Absorbed Repositories:** `Z:\repos\doc-chameleon`, `Z:\repos\ap-multitool-portal`  
**Execution Environment:** `chantecler-01` VPS (Linux)

---

## 1. Objective
Consolidate the standalone `doc-chameleon` (formatting verification engine) and `ap-multitool-portal` (web landing generator) repositories into the unified `ap-multitool` legal suite monorepo following the **`uv` Workspace Standard**.

---

## 2. Execution Sequence

### Phase 1: Native VPS Merge & History Rewrite
Execute [`ops/consolidate_monorepo.sh`](file:///Z:/repos/ap-multitool/ops/consolidate_monorepo.sh) on `chantecler-01`:
1. Creates branch `refactor/ap-multitool-monorepo-consolidation`.
2. Rewrites `doc-chameleon` commit history to live natively inside `packages/doc-chameleon/` and namespaces historical tags (`doc-chameleon/*`).
3. Purges pre-generated HTML pages, giant CSV inventory, and sitemaps from `ap-multitool-portal` history using `git-filter-repo`, rewrites history into `web/portal/`, and namespaces historical tags (`portal/*`).
4. Merges both histories into `ap-multitool`.
5. Moves `core/` to `packages/ap-core/src/ap_core/`, desktop app files to `apps/desktop/`, and CLI to `apps/cli/src/ap_cli/`.

### Phase 2: Manifest & Workspace Setup
1. Configure root `pyproject.toml` with `[tool.uv.workspace]`.
2. Ensure `packages/ap-core/pyproject.toml` and `packages/doc-chameleon/pyproject.toml` are recognized as workspace members.
3. Update `apps/desktop` and `apps/cli` to declare workspace dependencies on `ap-core` and `doc-chameleon`.

### Phase 3: Verification & Test Execution
Run on `chantecler-01`:
```bash
uv sync
uv run pytest
uv run python -m ap_cli.main --help
uv run python -m doc_chameleon.cli --help
```

### Phase 4: Sibling Repositories Archival
1. In `Z:\repos\doc-chameleon\README.md` and `Z:\repos\ap-multitool-portal\README.md`, commit the deprecation banner pointing to `ap-multitool`.
2. Set repositories to Read-Only on GitHub.
