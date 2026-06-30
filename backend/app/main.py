from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .company_brain.engine import process_intake, resolve_approval
from .company_brain.schemas import IntakeRequest, ResolveApprovalRequest
from .company_brain.store import store

LOCAL_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]

app = FastAPI(
    title="Company Brain Workbench API",
    description="Human corrections become reusable company memory.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=LOCAL_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/workflows/intake")
def intake(payload: IntakeRequest) -> dict:
    state = store.load()
    state, response = process_intake(state, payload.text)
    store.save(state)
    return response


@app.get("/api/approvals")
def approvals() -> dict:
    state = store.load()
    return {"approvals": [approval.model_dump() for approval in state.approvals]}


@app.post("/api/approvals/{approval_id}/resolve")
def resolve(approval_id: str, payload: ResolveApprovalRequest) -> dict:
    state = store.load()
    result = resolve_approval(state, approval_id, payload.decision, payload.rationale)
    if result is None:
        raise HTTPException(status_code=404, detail="approval not found")
    state, response = result
    store.save(state)
    return response


@app.get("/api/brain/rules")
def rules() -> dict:
    state = store.load()
    return {"rules": [rule.model_dump() for rule in state.rules]}


@app.get("/api/audit")
def audit() -> dict:
    state = store.load()
    return {"events": [event.model_dump() for event in state.audit]}


@app.post("/api/demo/reset")
def reset_demo() -> dict:
    state = store.reset()
    return state.model_dump()


@app.post("/api/demo/run")
def run_guided_demo() -> dict:
    state = store.reset()
    state, priya = process_intake(state, "Priya Sharma joins as a Sales Engineer in Dubai.")
    approval_id = priya["approval"]["id"]
    result = resolve_approval(state, approval_id, "Sales", "At this company, Sales Engineer belongs to Sales.")
    if result is None:
        raise HTTPException(status_code=500, detail="guided demo failed to resolve approval")
    state, resolution = result
    state, omar = process_intake(state, "Omar Reyes joins as a Sales Engineer in Dubai.")
    store.save(state)
    return {
        "steps": [
            {"label": "Priya escalated", "data": priya},
            {"label": "Human resolved", "data": resolution},
            {"label": "Omar auto-resolved", "data": omar},
        ],
        "state": state.model_dump(),
    }
