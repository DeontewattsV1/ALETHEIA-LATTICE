"""
Aletheia Lattice FastAPI Server.
POST /adjudicate  — evidence-bounded claim analysis
GET  /health      — liveness check
GET  /codex       — system statistics
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import time
import logging

from aletheia_lattice.evidence.channels import (
    TemporalEvidenceMesh, EvidenceClaim, ChannelType, ConfidenceLevel
)
from aletheia_lattice.immune.layer import SovereignImmuneLayer, GateState
from aletheia_lattice.reasoning.engine import ParallelReasoningEngine

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("aletheia.api")

app = FastAPI(
    title="Aletheia Lattice",
    description="Evidence-Bounded Sovereign AI — NIST AI RMF 1.0 Aligned",
    version="1.0.0",
)

# ── Global pipeline (process-scoped) ──────────────────────────────────────
_mesh    = TemporalEvidenceMesh()
_immune  = SovereignImmuneLayer()
_engine  = ParallelReasoningEngine()
_start   = time.time()
_calls   = {"total": 0, "condemned": 0, "caution": 0, "promoted": 0}


class AdjudicateRequest(BaseModel):
    claim:             str
    context:           Optional[Dict]   = None
    evidence_scores:   Optional[List[float]] = None
    retrieved_evidence:Optional[List[str]]   = None
    archive_evidence:  Optional[List[str]]   = None


class AdjudicateResponse(BaseModel):
    gate_state:          str
    promoted:            bool
    confidence:          float
    supporting_lanes:    List[str]
    contradiction_found: bool
    contradiction_detail:Optional[str]
    policy_violations:   List[str]
    uncertainty_notes:   List[str]
    formatted_output:    str
    latency_ms:          float


@app.post("/adjudicate", response_model=AdjudicateResponse)
async def adjudicate(req: AdjudicateRequest):
    t0 = time.perf_counter()
    _calls["total"] += 1

    # Step 1: Sovereign Immune Layer gate
    gate = _immune.evaluate(req.claim, req.context or {})
    if not gate.routable:
        _calls["condemned"] += 1
        return JSONResponse(
            status_code=400,
            content={
                "gate_state": gate.state.value,
                "reason": gate.reason,
                "message": _immune.format_refusal(gate.state, gate.reason),
            },
        )
    if gate.state == GateState.CAUTION:
        _calls["caution"] += 1

    # Step 2: Parallel Reasoning Engine
    output = _engine.reason(
        claim=req.claim,
        context=req.context,
        evidence_scores=req.evidence_scores,
        retrieved_evidence=req.retrieved_evidence,
        archive_evidence=req.archive_evidence,
    )

    if output.promoted:
        _calls["promoted"] += 1

    latency = (time.perf_counter() - t0) * 1000

    return AdjudicateResponse(
        gate_state=gate.state.value,
        promoted=output.promoted,
        confidence=output.confidence,
        supporting_lanes=output.supporting_lanes,
        contradiction_found=output.contradiction_found,
        contradiction_detail=output.contradiction_detail,
        policy_violations=output.policy_violations,
        uncertainty_notes=output.uncertainty_notes,
        formatted_output=output.format_output(),
        latency_ms=round(latency, 2),
    )


@app.get("/health")
async def health():
    return {"status": "ok", "uptime_seconds": round(time.time() - _start)}


@app.get("/codex")
async def codex():
    return {
        "total_adjudications": _calls["total"],
        "condemned":          _calls["condemned"],
        "caution":            _calls["caution"],
        "promoted":           _calls["promoted"],
        "evidence_stats":     _mesh.stats(),
        "uptime_seconds":     round(time.time() - _start),
    }


@app.exception_handler(Exception)
async def global_error_handler(req: Request, exc: Exception):
    log.error(f"Unhandled exception: {exc}")
    return JSONResponse(status_code=500, content={"error": "Internal server error"})
