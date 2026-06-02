Review the FastAPI route file at: $ARGUMENTS

Check for these specific issues:
- Business logic inside route handlers (should be in services/)
- Missing error handling (no try/except around service calls)
- Missing response_model on route decorators
- Sync functions instead of async
- Any direct DB calls (should go through services)
- Missing input validation in Pydantic schemas

Report each issue with: file, line number, issue type, suggested fix.
End with a score: CLEAN / NEEDS WORK / REFACTOR REQUIRED
