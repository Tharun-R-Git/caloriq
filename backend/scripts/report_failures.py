#!/usr/bin/env python3
"""Run pytest and file GitHub issues for every failing test."""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO_OWNER = "Tharun-R-Git"
REPO_NAME = "caloriq"
ASSIGNEE = "Tharun-R-Git"
LABELS = ["bug", "test-failure", "automated"]

REPORT_FILE = Path(__file__).parent.parent.parent / "test-report.json"

# Always use the venv Python so pytest-json-report is available regardless
# of which Python interpreter the caller (e.g. the Stop hook) uses.
_venv_scripts = Path(__file__).parent.parent / "venv" / "Scripts" / "python.exe"
_venv_bin     = Path(__file__).parent.parent / "venv" / "bin" / "python"
VENV_PYTHON   = str(_venv_scripts if _venv_scripts.exists() else _venv_bin if _venv_bin.exists() else sys.executable)


def run_tests() -> int:
    root = Path(__file__).parent.parent.parent
    result = subprocess.run(
        [
            VENV_PYTHON, "-m", "pytest", "backend/tests/",
            "--json-report",
            f"--json-report-file={REPORT_FILE}",
            "-q",
        ],
        cwd=root,
    )
    return result.returncode


def current_branch() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return out.strip()
    except Exception:
        return "unknown"


def ensure_labels(client: httpx.Client) -> None:
    existing_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/labels"
    resp = client.get(existing_url)
    existing = {lbl["name"] for lbl in resp.json()} if resp.is_success else set()

    label_meta = {
        "bug": {"color": "d73a4a", "description": "Something isn't working"},
        "test-failure": {"color": "e4e669", "description": "Automated test failed"},
        "automated": {"color": "0075ca", "description": "Created by automation"},
    }
    for name in LABELS:
        if name not in existing:
            client.post(
                existing_url,
                json={"name": name, **label_meta.get(name, {"color": "cccccc"})},
            )


def create_issue(client: httpx.Client, test: dict, branch: str, timestamp: str) -> dict:
    node_id: str = test.get("nodeid", "")
    name: str = node_id.split("::")[-1] if "::" in node_id else node_id

    # Extract error details from call phase
    call = test.get("call") or {}
    longrepr: str = call.get("longrepr") or test.get("longrepr") or ""

    # Location
    loc = test.get("location", {})
    file_path: str = loc[0] if isinstance(loc, list) and len(loc) > 0 else loc.get("file", "unknown")
    line_number: int = loc[1] if isinstance(loc, list) and len(loc) > 1 else loc.get("line", 0)

    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    body = f"""\
## Failing test
`{node_id}`

## Error
```
{longrepr.strip()}
```

## Location
File: `{file_path}`, Line: {line_number}

## Context
- Branch: `{branch}`
- Timestamp: {timestamp}
- Python: {py_version}
"""

    payload = {
        "title": f"Test failure: {name}",
        "body": body,
        "labels": LABELS,
        "assignees": [ASSIGNEE],
    }
    resp = client.post(
        f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues",
        json=payload,
    )
    resp.raise_for_status()
    return resp.json()


def main() -> int:
    exit_code = run_tests()

    if not REPORT_FILE.exists():
        print("No test report found — pytest may have failed to run.")
        return exit_code

    report = json.loads(REPORT_FILE.read_text())
    failed = [t for t in report.get("tests", []) if t.get("outcome") == "failed"]

    if not failed:
        print("All tests passing — no issues created")
        return 0

    if not GITHUB_TOKEN:
        print(f"WARNING: GITHUB_TOKEN not set — skipping issue creation for {len(failed)} failure(s).")
        for t in failed:
            print(f"  FAILED  {t.get('nodeid')}")
        return exit_code

    branch = current_branch()
    timestamp = datetime.now(timezone.utc).isoformat()

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    created = 0
    with httpx.Client(headers=headers, timeout=30) as client:
        ensure_labels(client)
        for test in failed:
            try:
                issue = create_issue(client, test, branch, timestamp)
                print(f"  Created issue #{issue['number']}: {issue['title']}")
                created += 1
            except httpx.HTTPStatusError as exc:
                print(f"  ERROR creating issue for {test.get('nodeid')}: {exc.response.status_code} {exc.response.text}")

    print(f"\nCreated {created} issues for {len(failed)} failing test(s)")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
