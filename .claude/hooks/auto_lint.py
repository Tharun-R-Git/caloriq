import sys, json, subprocess, os

try:
    data = json.load(sys.stdin)
    path = data.get('path', data.get('file_path', ''))
    if path.endswith('.py') and os.path.exists(path):
        subprocess.run(['ruff', 'check', '--fix', path, '--quiet'],
                      capture_output=True)
        subprocess.run(['ruff', 'format', path, '--quiet'],
                      capture_output=True)
        print(f"[LINT] Auto-linted: {path}")
except Exception:
    pass

sys.exit(0)
