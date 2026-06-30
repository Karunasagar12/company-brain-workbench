from __future__ import annotations

import json
from pathlib import Path
from threading import Lock

from .schemas import StoreState


class JsonStateStore:
    """Small local persistence layer for the MVP.

    Runtime JSON lives in backend/data and is gitignored. Writes are atomic to
    avoid partially written state when a dev server restarts mid-request.
    """

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path(__file__).resolve().parents[2] / "data" / "state.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def load(self) -> StoreState:
        with self._lock:
            if not self.path.exists():
                return StoreState()
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return StoreState.model_validate(data)

    def save(self, state: StoreState) -> StoreState:
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = self.path.with_suffix(".tmp")
            tmp_path.write_text(state.model_dump_json(indent=2), encoding="utf-8")
            tmp_path.replace(self.path)
            return state

    def reset(self) -> StoreState:
        return self.save(StoreState())


store = JsonStateStore()
