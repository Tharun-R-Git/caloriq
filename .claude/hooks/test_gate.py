import subprocess, sys, os

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
backend = os.path.join(root, 'backend')

if os.path.isdir(backend):
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 'tests/', '-q', '--tb=short'],
        cwd=backend,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print("[FAIL] TEST GATE FAILED -- fix tests before ending session", file=sys.stderr)
        print(result.stdout, file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(2)
    else:
        print("[OK] All tests passing")
        sys.exit(0)
