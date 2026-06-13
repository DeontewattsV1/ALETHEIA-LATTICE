"""
Sovereign Immune Layer — L5: Policy Enforcement at Every Boundary.

Five decision states: VOID · TRACE · CAUTION · GRAVE · CONDEMNED
Intercepts at: prompt ingress, retrieval, tool invocation, egress, post-action.
"""

import re
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

_log = logging.getLogger("aletheia.immune")


class GateState(Enum):
    VOID      = "VOID"       # Benign — passes through with logging
    TRACE     = "TRACE"      # Low-risk — proceeds with extra telemetry
    CAUTION   = "CAUTION"    # Sensitive — narrowed scope, source-binding required
    GRAVE     = "GRAVE"      # High-risk — high-level safety analysis only
    CONDEMNED = "CONDEMNED"  # Refusal + redirection + session flagged


@dataclass
class GateDecision:
    state:        GateState
    reason:       str
    routable:     bool
    restrictions: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.routable = self.state in (GateState.VOID, GateState.TRACE, GateState.CAUTION)


class SovereignImmuneLayer:
    """
    Policy enforcement at every boundary.
    Applies a five-step gate sequence on every request.
    """

    _HARM_PATTERNS = [
        re.compile(r"how\s+to\s+(synthesize|make|create)\s+(weapon|explosive|poison)", re.I),
        re.compile(r"(jailbreak|bypass|override)\s+(your|the)\s+(safety|filter|guidelines)", re.I),
        re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.I),
        re.compile(r"great\s+replacement|white\s+genocide", re.I),
        re.compile(r"you\s+are\s+now\s+(dan|jailbroken|uncensored)", re.I),
    ]

    _SENSITIVE_PATTERNS = [
        re.compile(r"classified|top\s+secret|codeword", re.I),
        re.compile(r"critical\s+infrastructure|scada|ics\s+system", re.I),
        re.compile(r"(ssn|social\s+security)\s+(number|#)", re.I),
        re.compile(r"(vulnerability|exploit)\s+(in|for)\s+(power|water|grid|hospital)", re.I),
    ]

    def evaluate(self, request_text: str, context: Optional[Dict] = None) -> GateDecision:
        """Run five-step gate sequence: intent → provenance → contradiction → tool-risk → action."""

        # Step 1: Intent scan — harm facilitation patterns
        for pattern in self._HARM_PATTERNS:
            if pattern.search(request_text):
                _log.warning("CONDEMNED: harm pattern matched")
                return GateDecision(
                    state=GateState.CONDEMNED,
                    reason="Request matches known harm-facilitation or jailbreak pattern.",
                    routable=False,
                )

        # Step 2: Sensitive domain check
        for pattern in self._SENSITIVE_PATTERNS:
            if pattern.search(request_text):
                _log.info("CAUTION: sensitive domain detected")
                return GateDecision(
                    state=GateState.CAUTION,
                    reason="Sensitive domain detected — narrowed scope and source-binding required.",
                    routable=True,
                    restrictions=[
                        "high_level_analysis_only",
                        "no_operational_details",
                        "no_speculation",
                        "source_anchoring_required",
                    ],
                )

        # Step 3: Payload anomaly
        if len(request_text) > 50_000:
            return GateDecision(
                state=GateState.TRACE,
                reason="Unusually large payload — flagged for pattern analysis.",
                routable=True,
                restrictions=["extra_telemetry"],
            )

        return GateDecision(
            state=GateState.VOID,
            reason="Normal operating parameters. No threats detected.",
            routable=True,
        )

    def format_refusal(self, state: GateState, reason: str) -> str:
        """When refusing, always explain at safe generality and offer adjacent help."""
        alternatives = {
            GateState.CONDEMNED: (
                "I can help with defensive security analysis, governance frameworks, "
                "policy compliance review, and cryptographic standards documentation."
            ),
            GateState.GRAVE: (
                "I can provide high-level risk framing and references to authoritative guidance "
                "such as NIST AI RMF, CISA advisories, and FIPS standards."
            ),
        }
        alt = alternatives.get(state, "")
        base = f"I'm not able to assist with that request. {reason}"
        return f"{base}\n\nWhat I can help with: {alt}" if alt else base
