import subprocess, sys, os

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
backend = os.path.join(root, 'backend')
report_script = os.path.join(backend, 'scripts', 'report_failures.py')

# Use the venv Python so httpx and pytest-json-report are available.
_venv_win = os.path.join(backend, 'venv', 'Scripts', 'python.exe')
_venv_unix = os.path.join(backend, 'venv', 'bin', 'python')
venv_python = _venv_win if os.path.exists(_venv_win) else _venv_unix if os.path.exists(_venv_unix) else sys.executable

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

        # Auto-file GitHub issues for failing tests
        if os.path.exists(report_script):
            print("[INFO] Filing GitHub issues for failing tests...", file=sys.stderr)
            subprocess.run([venv_python, report_script], cwd=root)

        sys.exit(2)
    else:
        print("[OK] All tests passing")
        sys.exit(0)
