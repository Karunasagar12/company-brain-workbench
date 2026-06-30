# Security Notes

This repository is a local product prototype. It is designed to demonstrate the Company Brain workflow without touching real enterprise systems.

## Current safeguards

- No real HR, IT, finance, Microsoft, payroll, or identity-provider integrations.
- Runtime JSON state is stored under `backend/data/` and ignored by git.
- `.env` and local frontend environment files are ignored by git.
- Backend CORS allows only localhost development origins by default.
- Workflow intake text is length-limited and rejects unsupported control characters.
- The UI renders data through React text nodes, not raw HTML injection.

## Before production use

- Replace local JSON persistence with a real database and migrations.
- Add authentication and role-based authorization to every state-changing endpoint.
- Add CSRF/session hardening if browser cookie auth is introduced.
- Add request rate limiting and structured security logging.
- Add secret scanning in CI.
- Perform dependency audits before deployment.

## Reporting

Please open a private issue or contact the maintainer directly for security concerns.
