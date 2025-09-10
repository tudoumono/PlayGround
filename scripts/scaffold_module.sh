#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: scripts/scaffold_module.sh <module_name>" >&2
  exit 1
fi

name="$1"
root_dir="$(cd "$(dirname "$0")/.." && pwd)"
tpl_dir="$root_dir/.scaffold/python-uv"
dest="$root_dir/$name"

if [ -e "$dest" ]; then
  echo "Error: $dest already exists" >&2
  exit 2
fi

mkdir -p "$dest"
cp -R "$tpl_dir/." "$dest/"

# プレースホルダを置換
rg -l "__MODULE_NAME__" "$dest" | while read -r f; do
  sed -i "s/__MODULE_NAME__/$name/g" "$f"
done

echo "Scaffolded $name at $dest"
echo "Next steps:"
echo "  cd $name"
echo "  uv venv && uv pip install -e .  # or uv sync"
