#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
usage: spawn.sh <name> <agy|claude|codex|...> [options] [-- <agent-args...>]

options:
  --tab              open in a new tab instead of splitting a pane in the current tab
  --tab-name NAME    open in the tab labelled NAME, creating it if missing
  --cwd PATH         working directory (default: $PWD)
  --task TEXT        prompt to send once the agent is ready
  --task-file FILE   read the prompt from FILE
  --report FILE      report file (default: <repo>/.herdr/reports/<name>.md when a task is given)
  --wait             wait for the agent to settle after the prompt
  --timeout MS       wait timeout (default: 600000)
  --max N            maximum live named agents in the workspace (default: 4)
EOF
  exit 2
}

pyjson() {
  PYTHONIOENCODING=utf-8 python -c "import sys, json, os
d = json.loads(sys.stdin.buffer.read())
$1" | tr -d '\r'
}

[ "${HERDR_ENV:-}" = 1 ] || { echo "not running inside a Herdr pane" >&2; exit 1; }
[ $# -ge 2 ] || usage

name=$1 kind=$2
shift 2
[[ $name =~ ^[a-z][a-z0-9_-]{0,31}$ ]] || { echo "invalid name: $name" >&2; exit 2; }

new_tab=0 tab_name="" cwd=$PWD task="" report="" wait=0 timeout=600000 max=4
agent_args=()
while [ $# -gt 0 ]; do
  case $1 in
    --tab) new_tab=1 ;;
    --tab-name) tab_name=$2; shift ;;
    --cwd) cwd=$2; shift ;;
    --task) task=$2; shift ;;
    --task-file) task=$(cat "$2"); shift ;;
    --report) report=$2; shift ;;
    --wait) wait=1 ;;
    --timeout) timeout=$2; shift ;;
    --max) max=$2; shift ;;
    --) shift; agent_args=("$@"); break ;;
    *) usage ;;
  esac
  shift
done

if [ -n "$task" ]; then
  [ -n "$report" ] || report="$(git -C "$cwd" rev-parse --show-toplevel 2>/dev/null || printf '%s' "$cwd")/.herdr/reports/$name.md"
  mkdir -p "$(dirname "$report")"
  rm -f "$report"
  report_native=$(cygpath -m "$report" 2>/dev/null || printf '%s' "$report")
  task+="

---
Khi kết thúc (xong hoặc không làm được), ghi báo cáo vào file: $report_native
- Nội dung: kết quả, file đã sửa, việc còn dở, điều cần người quyết.
- Dòng cuối cùng của file phải đúng một trong hai: \`STATUS: done\` hoặc \`STATUS: failed\`.
- Chỉ ghi dòng STATUS khi báo cáo đã hoàn chỉnh."
fi

live=$(herdr agent list | pyjson '
print(sum(1 for a in d["result"]["agents"]
          if a.get("name") and a["workspace_id"] == os.environ["HERDR_WORKSPACE_ID"]))')
if [ "$live" -ge "$max" ]; then
  echo "limit reached: $live live named agents in workspace (max $max)" >&2
  exit 3
fi

split_largest() {
  read -r target width height < <(herdr pane layout --pane "$1" | pyjson '
l = d["result"]["layout"]
p = max(l["panes"], key=lambda p: p["rect"]["width"] * p["rect"]["height"])
print(p["pane_id"], p["rect"]["width"], p["rect"]["height"])')
  if [ "$width" -gt $((height * 2)) ]; then direction=right; else direction=down; fi
  herdr pane split --pane "$target" --direction "$direction" --cwd "$cwd" --no-focus | pyjson 'print(d["result"]["pane"]["pane_id"])'
}

create_tab() {
  herdr tab create --workspace "$HERDR_WORKSPACE_ID" --cwd "$cwd" --label "$1" --no-focus | pyjson 'print(d["result"]["root_pane"]["pane_id"])'
}

if [ -n "$tab_name" ]; then
  tab_id=$(herdr tab list --workspace "$HERDR_WORKSPACE_ID" | TAB_NAME="$tab_name" pyjson '
print(next((t["tab_id"] for t in d["result"]["tabs"] if t["label"] == os.environ["TAB_NAME"]), ""))')
  if [ -n "$tab_id" ]; then
    anchor=$(herdr pane list --workspace "$HERDR_WORKSPACE_ID" | TAB_ID="$tab_id" pyjson '
print(next(p["pane_id"] for p in d["result"]["panes"] if p["tab_id"] == os.environ["TAB_ID"]))')
    pane=$(split_largest "$anchor")
  else
    pane=$(create_tab "$tab_name")
  fi
elif [ $new_tab = 1 ]; then
  pane=$(create_tab "$name")
else
  pane=$(split_largest "$HERDR_PANE_ID")
fi

fail() { echo "$1" >&2; echo "name=$name pane=$pane kind=$kind status=failed" >&2; exit 1; }

herdr pane rename "$pane" "$name" >/dev/null
out=$(herdr agent start "$name" --kind "$kind" --pane "$pane" --timeout 60000 ${agent_args[@]+-- "${agent_args[@]}"} 2>&1) || fail "$out"

if [ -n "$task" ]; then
  prompt_args=()
  [ $wait = 1 ] && prompt_args=(--wait --timeout "$timeout")
  out=$(herdr agent prompt "$name" "$task" ${prompt_args[@]+"${prompt_args[@]}"} 2>&1) || fail "$out"
fi

echo "name=$name pane=$pane kind=$kind${report:+ report=$report}"
