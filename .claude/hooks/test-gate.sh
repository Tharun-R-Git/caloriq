#!/bin/bash
# Stop hook: block session end if backend tests are failing
cd "$(git rev-parse --show-toplevel 2>/dev/null || echo '.')"

echo "Running test gate before session end..."

if [ -d "backend" ]; then
    cd backend
    result=$(python -m pytest tests/ -q --tb=short 2>&1)
    exit_code=$?

    if [ $exit_code -ne 0 ]; then
        echo "❌ TEST GATE FAILED — Claude cannot end session until tests pass"
        echo ""
        echo "$result"
        echo ""
        echo "Fix the failing tests first, then end the session."
        exit 1
    else
        echo "✅ All tests passing — session end allowed"
        exit 0
    fi
fi

exit 0
