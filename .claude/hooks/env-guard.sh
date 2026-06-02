#!/bin/bash
# PreToolUse hook: block any writes to .env files
# Claude Code passes tool input as JSON via stdin

input=$(cat)
file_path=$(echo "$input" | python -c "
import sys, json
data = json.load(sys.stdin)
print(data.get('path', data.get('file_path', '')))
" 2>/dev/null)

if echo "$file_path" | grep -qE '\.env$|\.env\.'; then
    echo "🚫 ENV GUARD: Direct edits to .env files are blocked."
    echo "   File: $file_path"
    echo "   Reason: API keys and secrets must be managed manually."
    echo "   To update: edit .env directly in your editor, never via Claude."
    exit 1
fi

exit 0
