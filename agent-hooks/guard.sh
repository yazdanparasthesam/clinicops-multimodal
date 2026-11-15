#!/usr/bin/env bash
# Guard: block dangerous patterns for coding agents
if echo "$1" | grep -qE "rm -rf|cat.*\.env|force-push|prod.*write"; then
  echo "BLOCKED by guard.sh: $1"
  exit 1
fi
exit 0
