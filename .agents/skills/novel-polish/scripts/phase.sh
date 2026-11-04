#!/usr/bin/env bash
# usage: phase.sh <slug> <start> [--name orch-pl] [các tuỳ chọn của gen_briefs.py...]
# Đóng pane orchestrator cũ cùng tên, sinh brief, rồi spawn orchestrator mới.
set -e
cd "$(dirname "$0")/../../../.."
slug=$1 start=$2; shift 2
name=orch-pl
if [ "$1" = "--name" ]; then name=$2; shift 2; fi
F=$(python .agents/skills/novel-polish/scripts/gen_briefs.py "$slug" "$start" "$@")
p=$(herdr agent list | python -c "import sys,json;print(' '.join(x['pane_id'] for x in json.load(sys.stdin)['result']['agents'] if x.get('name')=='$name'))" | tr -d '\r')
for x in $p; do herdr pane close "$x" >/dev/null; done
[ -f ".herdr/reports/$name.md" ] && mv ".herdr/reports/$name.md" ".herdr/reports/$name-prev.md"
git log -1 --format=%h > "${F%.md}.base"
echo "task=$F base=$(cat "${F%.md}.base")"
bash .agents/skills/herdr-spawn/scripts/spawn.sh "$name" agy --task-file "$F" --max 8 -- --model gemini-4-argon-medium --dangerously-skip-permissions
