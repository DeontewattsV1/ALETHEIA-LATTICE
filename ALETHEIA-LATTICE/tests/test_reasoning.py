"""Tests for Parallel Reasoning Engine — L3."""
from aletheia_lattice.reasoning.engine import ParallelReasoningEngine, LaneResult

def test_clean_claim_with_evidence_promotes():
    engine = ParallelReasoningEngine()
    output = engine.reason(
        claim="FIPS 203 ML-KEM is the baseline for key encapsulation",
        evidence_scores=[0.95, 0.90],
        retrieved_evidence=["FIPS 203 is the NIST standard for ML-KEM key encapsulation."],
    )
    assert output.promoted is True
    assert output.confidence >= 0.7

def test_claim_without_evidence_not_promoted():
    engine = ParallelReasoningEngine()
    output = engine.reason(
        claim="Some unsupported speculative claim about future events",
        evidence_scores=[],
        retrieved_evidence=[],
    )
    assert output.promoted is False

def test_contradicted_claim_not_promoted():
    engine = ParallelReasoningEngine()
    output = engine.reason(
        claim="RSA-2048 is secure against quantum computers",
        evidence_scores=[0.8],
        retrieved_evidence=["RSA-2048 is discussed in quantum context"],
        archive_evidence=["RSA-2048 is not secure — Shor\'s algorithm can break it on a sufficiently large quantum processor"],
    )
    assert output.contradiction_found is True
    assert output.promoted is False

def test_constraint_violation_blocks_promotion():
    engine = ParallelReasoningEngine()
    output = engine.reason(
        claim="Migrate short-lived tokens before long-lived secrets",
        context={"policy_rules": [{"keyword": "short-lived", "blocked": True, "reason": "Sequence violation"}]},
        evidence_scores=[0.9],
    )
    assert len(output.policy_violations) > 0
    assert output.promoted is False

def test_output_has_all_fields():
    engine = ParallelReasoningEngine()
    output = engine.reason("Any claim", evidence_scores=[0.7])
    assert hasattr(output, "promoted")
    assert hasattr(output, "confidence")
    assert hasattr(output, "supporting_lanes")
    assert hasattr(output, "contradiction_found")
    assert output.format_output()
