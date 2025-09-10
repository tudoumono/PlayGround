#!/bin/bash
# Project-scoped MCP launcher for Excel
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" >/dev/null 2>&1; pwd -P)"
PROJ_ROOT="$(cd -- "${SCRIPT_DIR}/.." >/dev/null 2>&1; pwd -P)"

if [ -f "${PROJ_ROOT}/.env" ]; then
  # shellcheck disable=SC2046
  export $(grep -v '^#' "${PROJ_ROOT}/.env" | xargs)
fi

exec cipher --mode mcp

