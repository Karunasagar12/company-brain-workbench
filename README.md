<div align="center">

# Company Brain Workbench

### Corrected once. Never asks again.

</div>

---

AI employees fail when they ask the same question twice.

Company Brain Workbench turns human corrections into structured decision memory, so future workflows resolve automatically instead of escalating again.

## Demo in 60 Seconds

1. **Priya Sharma joins as a Sales Engineer in Dubai.** The system detects that the role can map to Sales or Engineering and refuses to guess.
2. **A human resolves the ambiguity once.** Sales Engineer maps to Sales for this company, creating a reusable Company Brain rule.
3. **Omar Reyes joins as a Sales Engineer in Dubai.** The rule fires automatically. No human escalation is needed.

## What This Demonstrates

- Human-in-the-loop exception handling
- Persistent company-specific decision memory
- Rule matching for future auto-resolution
- Approval queue for ambiguous work
- Audit trail for enterprise trust
- A guided product demo optimized for a short walkthrough

## Tech Stack

| Layer | Stack |
|---|---|
| Frontend | Next.js, React, TypeScript |
| Backend | FastAPI, Python, Pydantic |
| Persistence | JSON-backed local store for the MVP |
| Testing | Pytest |
| Security posture | No committed secrets, explicit CORS origins, input length checks, local-only runtime state |

## Run Locally

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend docs:

```text
http://127.0.0.1:8000/docs
```

### Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:3000
```

## Demo Flow

Use the **Run guided demo** button to execute:

```text
Reset demo → Priya ambiguity → human resolution → brain rule created → Omar auto-resolved
```

## API Surface

```text
POST /api/workflows/intake
GET  /api/approvals
POST /api/approvals/{approval_id}/resolve
GET  /api/brain/rules
GET  /api/audit
POST /api/demo/reset
POST /api/demo/run
```

## Security Notes

- Runtime data lives under `backend/data/` and is ignored by git.
- `.env` files are ignored.
- CORS is restricted to localhost development origins by default.
- Incoming workflow text is length-limited.
- The MVP does not call real HR, IT, finance, Microsoft, or payroll systems.

## Product Thesis

The moat is not one AI agent. The moat is the company-specific decision memory that compounds across every workflow.
