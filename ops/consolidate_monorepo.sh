#!/usr/bin/env bash
# ==============================================================================
# consolidate_monorepo.sh — ap-multitool Legal Suite Monorepo Consolidation
#
# Execution Environment: chantecler-01 VPS (Native Linux)
# ==============================================================================

set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"

REPO="ap-multitool"
WORKTREE_PATH="/home/aewoodyard/repos/ap-multitool"
BRANCH_NAME="refactor/ap-multitool-monorepo-consolidation"

echo "=== STAX Fleet Monorepo Consolidation ==="
echo "Repo:          ${REPO}"
echo "Worktree Path: ${WORKTREE_PATH}"
echo "Branch:        ${BRANCH_NAME}"
echo "========================================="

cd "${WORKTREE_PATH}"

git checkout master
git checkout -B "${BRANCH_NAME}"

# Clean up any leftover remotes
git remote remove remote-doc-chameleon 2>/dev/null || true
git remote remove remote-ap-portal 2>/dev/null || true

TMP_DIR="$(mktemp -d /tmp/ap-consolidation-XXXXXX)"
echo "Staging directory: ${TMP_DIR}"

DOC_CHAMELEON_SRC="/home/aewoodyard/repos/doc-chameleon"
AP_PORTAL_SRC="/home/aewoodyard/repos/ap-multitool-portal"

# 1. Process doc-chameleon history
echo "==> Cloning and filtering doc-chameleon..."
git clone "${DOC_CHAMELEON_SRC}" "${TMP_DIR}/doc-chameleon-staging"
(
    cd "${TMP_DIR}/doc-chameleon-staging"
    git tag -l | while read -r tag; do
        if [ -n "$tag" ]; then
            git tag "doc-chameleon/${tag}" "$tag"
            git tag -d "$tag"
        fi
    done
    git-filter-repo --to-subdirectory-filter packages/doc-chameleon --force
)

# 2. Process ap-multitool-portal history (purge bloat, filter to web/portal)
echo "==> Cloning and filtering ap-multitool-portal (purging bloat)..."
git clone "${AP_PORTAL_SRC}" "${TMP_DIR}/ap-portal-staging"
(
    cd "${TMP_DIR}/ap-portal-staging"
    git tag -l | while read -r tag; do
        if [ -n "$tag" ]; then
            git tag "portal/${tag}" "$tag"
            git tag -d "$tag"
        fi
    done
    git-filter-repo --invert-paths \
        --path pages \
        --path Landing_Pages_Inventory.csv \
        --path sitemap.xml \
        --path squarespace_ab_tests \
        --path blog \
        --path faq \
        --force
    git-filter-repo --to-subdirectory-filter web/portal --force
)

# 3. Merge sequentially into ap-multitool
echo "==> Merging doc-chameleon history into ${BRANCH_NAME}..."
git remote add remote-doc-chameleon "${TMP_DIR}/doc-chameleon-staging"
git fetch remote-doc-chameleon
git merge remote-doc-chameleon/main --allow-unrelated-histories -m "chore: merge doc-chameleon with full commit history" --no-edit
git remote remove remote-doc-chameleon

echo "==> Merging ap-multitool-portal history into ${BRANCH_NAME}..."
git remote add remote-ap-portal "${TMP_DIR}/ap-portal-staging"
git fetch remote-ap-portal
git merge remote-ap-portal/main --allow-unrelated-histories -m "chore: merge ap-multitool-portal with full commit history" --no-edit
git remote remove remote-ap-portal

rm -rf "${TMP_DIR}"

# 4. Restructure ap-multitool source directories
echo "==> Restructuring source trees..."

mkdir -p packages/ap-core/src/ap_core
if [ -d "core" ]; then
    git mv core/* packages/ap-core/src/ap_core/ || true
    rmdir core || true
fi

mkdir -p apps/desktop
for item in gui_apmultitool_qt.py apmultitool_qt ap_multitool.spec logo_small.png water_texture.png; do
    if [ -e "$item" ]; then
        git mv "$item" apps/desktop/
    fi
done

mkdir -p apps/cli/src/ap_cli
if [ -f "cli.py" ]; then
    git mv cli.py apps/cli/src/ap_cli/main.py
fi

if [ -d "web_portal" ]; then
    git rm -rf web_portal
fi

echo "============================================================"
echo "SUCCESS: Monorepo commit histories merged & tree restructured!"
echo "============================================================"
