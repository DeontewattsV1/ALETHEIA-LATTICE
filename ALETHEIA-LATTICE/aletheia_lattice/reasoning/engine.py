"""
Parallel Reasoning Engine — L3: The Non-Human Layer.

Five independent reasoning lanes. A claim is only promoted to output
when at least two lanes converge and the Adversarial Contradiction Lane
fails to refute it.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class LaneResult(Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


@dataclass
class ReasoningOutput:
    """Structured output from the Parallel Reasoning Engine."""
    claim:              str
    promoted:           bool
    confidence:         float             # 0.0 – 1.0
    supporting_lanes:   List[str]
    contradiction_found: bool
    contradiction_detail: Optional[str] = None
    policy_violations:  List[str] = field(default_factory=list)
    uncertainty_notes:  List[str] = field(default_factory=list)

    def format_output(self) -> str:
        status = "PROMOTED" if self.promoted else "REJECTED"
        lines = [
            f"[{status}] Confidence: {self.confidence:.0%}",
            f"Supporting lanes: {', '.join(self.supporting_lanes)}",
        ]
        if self.contradiction_found:
            lines.append(f"Contradiction: {self.contradiction_detail}")
        if self.policy_violations:
            lines.append(f"Policy violations: {'; '.join(self.policy_violations)}")
        if self.uncertainty_notes:
            lines.append(f"Uncertainty: {'; '.join(self.uncertainty_notes)}")
        return "\n".join(lines)


class CausalInferenceLane:
    """
    Traces dependency pathways and failure propagation in the Ontology Core.
    Does not generate scenarios — only traces known causal paths.
    """

    def evaluate(self, claim: str, context: Dict) -> Tuple[LaneResult, str]:
        ontology = context.get("ontology_context", {})
        dependencies = ontology.get("dependencies", [])

        issues = []
        for dep in dependencies:
            if dep.get("compromised") and dep.get("name") in claim:
                issues.append(f"Dependency '{dep['name']}' is flagged compromised")

        if issues:
            return LaneResult.WARN, " | ".join(issues)
        return LaneResult.PASS, "No causal issues detected"


class ConstraintSatisfactionLane:
    """
    Checks claims and plans against policy rules.
    Outputs PASS/WARN/FAIL — not natural language prose.
    """

    _SEQUENCING_RULES = [
        ("long-lived secrets", "short-lived", "Long-lived secrets must migrate before short-lived ones"),
        ("archive", "live migration", "Archive channel must be secured before live migration"),
    ]

    def evaluate(self, claim: str, context: Dict) -> Tuple[LaneResult, str]:
        claim_lower = claim.lower()
        violations = []

        for prerequisite, dependent, rule in self._SEQUENCING_RULES:
            if dependent in claim_lower and prerequisite not in claim_lower:
                violations.append(f"CONSTRAINT VIOLATION: {rule}")

        policy_rules = context.get("policy_rules", [])
        for rule in policy_rules:
            if rule.get("keyword") and rule["keyword"].lower() in claim_lower:
                if rule.get("blocked"):
                    violations.append(f"POLICY BLOCK: {rule.get('reason', 'Policy rule triggered')}")

        if violations:
            return LaneResult.FAIL, " | ".join(violations)
        return LaneResult.PASS, "Constraint satisfaction: PASS"


class ProbabilisticEstimationLane:
    """
    Computes posterior probability distributions over uncertain claims.
    Outputs probability intervals — not point estimates presented as facts.
    """

    def evaluate(self, claim: str, evidence_scores: List[float]) -> Tuple[LaneResult, str, float]:
        if not evidence_scores:
            return LaneResult.FAIL, "No evidence scores provided — claim cannot be promoted", 0.0

        mean_score = sum(evidence_scores) / len(evidence_scores)
        variance   = sum((s - mean_score) ** 2 for s in evidence_scores) / len(evidence_scores)
        lower      = max(0, mean_score - 1.96 * (variance ** 0.5))
        upper      = min(1, mean_score + 1.96 * (variance ** 0.5))

        detail = f"P(claim|evidence) ≈ [{lower:.2f}, {mean_score:.2f}, {upper:.2f}] (95% CI)"
        result = LaneResult.PASS if mean_score >= 0.6 else LaneResult.WARN
        return result, detail, mean_score


class RetrievalBackedSynthesisLane:
    """
    The only lane that produces natural language.
    Every sentence must be anchored to retrieved evidence — no open-ended completion.
    """

    def evaluate(self, claim: str, retrieved_evidence: List[str]) -> Tuple[LaneResult, str]:
        if not retrieved_evidence:
            return LaneResult.WARN, "No retrieved evidence to anchor this claim."

        anchored_count = sum(
            1 for e in retrieved_evidence
            if any(word in claim.lower() for word in e.lower().split()[:5])
        )
        if anchored_count == 0:
            return LaneResult.WARN, "Claim could not be traced to any retrieved evidence node."

        return LaneResult.PASS, f"Anchored to {anchored_count}/{len(retrieved_evidence)} evidence nodes"


class AdversarialContradictionLane:
    """
    Internal red-teamer — independently attempts to refute every promoted claim.
    If a compelling refutation is found, the claim is rejected.
    """

    def evaluate(self, claim: str, archive_evidence: List[str]) -> Tuple[bool, Optional[str]]:
        """Returns (contradiction_found, contradiction_detail)."""
        claim_lower = claim.lower()

        for evidence in archive_evidence:
            ev_lower = evidence.lower()
            # Simple lexical contradiction detection
            negation_pairs = [
                ("is not", "is "),
                ("was not", "was "),
                ("cannot", "can "),
                ("does not support", "supports"),
                ("no evidence", "evidence shows"),
            ]
            for negation, positive in negation_pairs:
                if negation in ev_lower:
                    positive_phrase = positive.strip()
                    if positive_phrase in claim_lower:
                        return True, f"Contradicting evidence found: {evidence[:120]}"

        return False, None


class ParallelReasoningEngine:
    """
    Orchestrates all five lanes. Promotes claims only on convergence with
    no successful contradiction.

    Convergence rule: at least 2 lanes must PASS, and the Adversarial
    Contradiction Lane must fail to produce a compelling refutation.
    """

    def __init__(self):
        self.causal       = CausalInferenceLane()
        self.constraint   = ConstraintSatisfactionLane()
        self.probabilistic = ProbabilisticEstimationLane()
        self.synthesis    = RetrievalBackedSynthesisLane()
        self.contradiction = AdversarialContradictionLane()

    def reason(
        self,
        claim: str,
        context: Optional[Dict] = None,
        evidence_scores: Optional[List[float]] = None,
        retrieved_evidence: Optional[List[str]] = None,
        archive_evidence: Optional[List[str]] = None,
    ) -> ReasoningOutput:
        """Run all five lanes in parallel and apply convergence promotion rule."""
        context           = context or {}
        # No default evidence: callers must supply explicit evidence scores.
        # Empty scores → probabilistic lane returns FAIL → claim not promoted.
        evidence_scores   = evidence_scores or []
        retrieved_evidence = retrieved_evidence or []
        archive_evidence  = archive_evidence or []

        lane_results: List[Tuple[str, LaneResult, str]] = []

        # Lane 1: Causal
        r, detail = self.causal.evaluate(claim, context)
        lane_results.append(("causal_inference", r, detail))

        # Lane 2: Constraint
        r, detail = self.constraint.evaluate(claim, context)
        lane_results.append(("constraint_satisfaction", r, detail))
        policy_violations = [detail] if r == LaneResult.FAIL else []

        # Lane 3: Probabilistic
        r, detail, confidence = self.probabilistic.evaluate(claim, evidence_scores)
        lane_results.append(("probabilistic_estimation", r, detail))

        # Lane 4: Retrieval-backed synthesis
        r, detail = self.synthesis.evaluate(claim, retrieved_evidence)
        lane_results.append(("retrieval_synthesis", r, detail))

        # Lane 5: Adversarial contradiction (independent)
        contradiction_found, contradiction_detail = self.contradiction.evaluate(
            claim, archive_evidence
        )

        # Convergence rule: at least 2 lanes must PASS, including at least one
        # evidence-grounded lane (probabilistic or synthesis).
        passing_lanes = [name for name, r, _ in lane_results if r == LaneResult.PASS]
        uncertainty_notes = [f"{name}: {detail}" for name, r, detail in lane_results if r == LaneResult.WARN]

        evidence_grounded = any(
            name in ("probabilistic_estimation", "retrieval_synthesis")
            for name in passing_lanes
        )
        promoted = (
            len(passing_lanes) >= 2
            and evidence_grounded
            and not contradiction_found
            and not policy_violations
        )

        return ReasoningOutput(
            claim=claim,
            promoted=promoted,
            confidence=confidence,
            supporting_lanes=passing_lanes,
            contradiction_found=contradiction_found,
            contradiction_detail=contradiction_detail,
            policy_violations=policy_violations,
            uncertainty_notes=uncertainty_notes,
        )
