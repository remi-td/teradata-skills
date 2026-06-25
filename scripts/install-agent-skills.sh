#!/usr/bin/env bash
# Install or update Teradata marketplace skills for agent runtimes.
#
# Hermes support materializes a flat SKILL.md tree and registers it through
# skills.external_dirs, keeping generated files out of ~/.hermes/skills.
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"

AGENT="hermes"
COMMAND="install"
MODE="copy"
ONLY=""
CONFIGURE_HERMES=1
MANIFEST="$REPO_ROOT/.claude-plugin/marketplace.json"
CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/teradata-skills/repos"
OUT_BASE="${XDG_DATA_HOME:-$HOME/.local/share}/teradata-skills"
OUT_DIR=""
JSON=0

usage() {
  cat <<'EOF'
Usage: scripts/install-agent-skills.sh [install|update|status] [options]

Options:
  --agent <hermes>        Target agent runtime (currently: hermes; default)
  --mode <copy|symlink>   Materialization mode (default: copy)
  --only a,b,c            Materialize only selected skill names
  --manifest <path>       Marketplace manifest (default: .claude-plugin/marketplace.json)
  --cache-dir <path>      Git clone cache (default: ~/.cache/teradata-skills/repos)
  --out-dir <path>        Flat skills output directory
  --no-configure          Do not edit Hermes config.yaml
  --json                  Print materializer JSON output
  -h, --help              Show this help

Examples:
  scripts/install-agent-skills.sh --agent hermes
  scripts/install-agent-skills.sh update --agent hermes
  scripts/install-agent-skills.sh --agent hermes --only teradata-react --mode symlink
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    install|update|status) COMMAND="$1"; shift ;;
    --agent) AGENT="$2"; shift 2 ;;
    --mode) MODE="$2"; shift 2 ;;
    --only) ONLY="$2"; shift 2 ;;
    --manifest) MANIFEST="$2"; shift 2 ;;
    --cache-dir) CACHE_DIR="$2"; shift 2 ;;
    --out-dir) OUT_DIR="$2"; shift 2 ;;
    --no-configure) CONFIGURE_HERMES=0; shift ;;
    --json) JSON=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

case "$AGENT" in
  hermes) ;;
  *) echo "Unsupported agent '$AGENT'. This installer currently supports: hermes" >&2; exit 2 ;;
esac

if [[ -z "$OUT_DIR" ]]; then
  OUT_DIR="$OUT_BASE/$AGENT/skills"
fi

if [[ "$COMMAND" == "status" ]]; then
  exec python3 "$SCRIPT_DIR/materialize_skills.py" status --out-dir "$OUT_DIR"
fi

materialize_args=(
  "$COMMAND"
  --repo-root "$REPO_ROOT"
  --manifest "$MANIFEST"
  --cache-dir "$CACHE_DIR"
  --out-dir "$OUT_DIR"
  --mode "$MODE"
)

if [[ -n "$ONLY" ]]; then
  materialize_args+=(--only "$ONLY")
fi
if [[ "$JSON" -eq 1 ]]; then
  materialize_args+=(--json)
fi

python3 "$SCRIPT_DIR/materialize_skills.py" "${materialize_args[@]}"

if [[ "$AGENT" == "hermes" && "$CONFIGURE_HERMES" -eq 1 ]]; then
  python3 "$SCRIPT_DIR/configure_hermes_external_dir.py" "$OUT_DIR" || {
    echo "Could not update Hermes config automatically." >&2
    echo "Add this directory to skills.external_dirs manually: $OUT_DIR" >&2
    exit 1
  }
  echo
  echo "Hermes skills are available from: $OUT_DIR"
  echo "Restart Hermes or run /reload-skills in an existing session."
fi
