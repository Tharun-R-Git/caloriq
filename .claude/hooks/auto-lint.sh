#!/bin/bash
# PostToolUse hook: auto-run ruff on any Python file Claude edits
# Claude Code passes tool result as JSON via stdin

input=$(cat)
file_path=$(echo "$input" | python -c "
import sys, json
data = json.load(sys.stdin)
print(data.get('path', data.get('file_path', '')))
" 2>/dev/null)

if echo "$file_path" | grep -qE '\.py$'; then
    if command -v ruff &> /dev/null; then
        echo "🔧 Auto-linting: $file_path"
        ruff check --fix "$file_path" --quiet
        ruff format "$file_path" --quiet
    fi
fi

exit 0
