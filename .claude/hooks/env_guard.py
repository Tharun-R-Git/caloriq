import sys, json

try:
    data = json.load(sys.stdin)
    path = data.get('path', data.get('file_path', ''))
    if '.env' in path.replace('\\', '/').split('/')[-1]:
        if path.endswith('.env') or '/.env.' in path.replace('\\', '/'):
            print(f"[BLOCKED] ENV GUARD: Blocked write to {path}")
            print("Edit .env manually in your editor — never via Claude.")
            sys.exit(1)
except Exception:
    pass

sys.exit(0)
