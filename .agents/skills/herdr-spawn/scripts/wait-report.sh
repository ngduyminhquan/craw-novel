#!/usr/bin/env bash
set -uo pipefail

usage() {
  cat <<'EOF'
usage: wait-report.sh <name> [report-file] [--timeout SEC] [--idle-grace SEC] [--interval SEC]

prints one line "name=<name> status=<status> report=<file>" and exits when:
  done | failed     the report ends with "STATUS: done" or "STATUS: failed"
  blocked           the agent is waiting on an approval or question
  idle-no-report    the agent stayed idle longer than --idle-grace without a finished report
  gone              the agent is no longer live
  timeout           --timeout elapsed
EOF
  exit 2
}

[ $# -ge 1 ] || usage
name=$1
shift
report="$(git rev-parse --show-toplevel 2>/dev/null || pwd)/.herdr/reports/$name.md"
if [ $# -gt 0 ] && [[ $1 != --* ]]; then report=$1; shift; fi
timeout=3600 idle_grace=60 interval=5
while [ $# -gt 0 ]; do
  case $1 in
    --timeout) timeout=$2; shift ;;
    --idle-grace) idle_grace=$2; shift ;;
    --interval) interval=$2; shift ;;
    *) usage ;;
  esac
  shift
done

finish() { echo "name=$name status=$1 report=$report"; exit 0; }

report_status() {
  [ -f "$report" ] || return 1
  local last
  last=$(tr -d '\r' < "$report" | sed '/^[[:space:]]*$/d' | tail -n 1)
  [[ $last =~ ^[[:space:]\`]*STATUS:[[:space:]]*(done|failed) ]] || return 1
  echo "${BASH_REMATCH[1]}"
}

start=$SECONDS idle_since=""
while :; do
  if status=$(report_status); then finish "$status"; fi

  agent_status=$(herdr agent get "$name" 2>/dev/null | PYTHONIOENCODING=utf-8 python -c '
import sys, json
print(json.loads(sys.stdin.buffer.read())["result"]["agent"]["agent_status"])' 2>/dev/null | tr -d '\r')

  case $agent_status in
    "") if status=$(report_status); then finish "$status"; fi; finish gone ;;
    blocked) finish blocked ;;
    idle|done)
      idle_since=${idle_since:-$SECONDS}
      [ $((SECONDS - idle_since)) -ge "$idle_grace" ] && finish idle-no-report ;;
    *) idle_since="" ;;
  esac

  [ $((SECONDS - start)) -ge "$timeout" ] && finish timeout
  sleep "$interval"
done
