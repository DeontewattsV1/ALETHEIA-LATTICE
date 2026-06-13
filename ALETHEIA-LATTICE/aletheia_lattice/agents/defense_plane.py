"""
Agentic Defense Plane — L4: "Propose and Coordinate" Layer.

Bounded agents that monitor, triage, and coordinate defense operations.
PROPOSE only — no consequential action without explicit human approval gate.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

_log = logging.getLogger("aletheia.agents")


class AgentMode(Enum):
    ADVISORY   = "advisory"    # Observe, retrieve, summarize, recommend only
    ASSISTED   = "assisted"    # Prepare actions for human approval
    READ_ONLY  = "read_only"   # Read and report — no action proposals


@dataclass
class AgentRecommendation:
    """A proposal from an agent — not a decision or command."""
    agent_name:       str
    action_proposed:  str
    supporting_evidence: List[str]
    expected_effect:  str
    risk_factors:     List[str]
    alternative:      Optional[str]
    requires_approval: bool = True   # Always True for consequential actions

    def format(self) -> str:
        lines = [
            f"[RECOMMENDATION — {self.agent_name}]",
            f"Proposed action: {self.action_proposed}",
            f"Expected effect: {self.expected_effect}",
        ]
        if self.risk_factors:
            lines.append(f"Risks: {'; '.join(self.risk_factors)}")
        if self.alternative:
            lines.append(f"Alternative: {self.alternative}")
        lines.append(f"Human approval required: {self.requires_approval}")
        return "\n".join(lines)


class BoundedAgent:
    """Base class for all L4 agents. Ephemeral credentials, tool-scoped permissions."""

    def __init__(self, name: str, mode: AgentMode = AgentMode.ADVISORY):
        self.name   = name
        self.mode   = mode
        self._log   = logging.getLogger(f"aletheia.agents.{name}")
        self._reads = 0
        self._budget_reads = 50  # Action budget per task window

    def _check_budget(self) -> bool:
        if self._reads >= self._budget_reads:
            self._log.warning(f"{self.name}: read budget exhausted — re-authorization required")
            return False
        self._reads += 1
        return True

    def propose(self, action: str, evidence: List[str], effect: str,
                risks: Optional[List[str]] = None, alternative: Optional[str] = None
                ) -> AgentRecommendation:
        return AgentRecommendation(
            agent_name=self.name,
            action_proposed=action,
            supporting_evidence=evidence,
            expected_effect=effect,
            risk_factors=risks or [],
            alternative=alternative,
            requires_approval=True,
        )


class WatchfloorAgent(BoundedAgent):
    """
    Continuously monitors network telemetry and threat feed updates.
    Produces ranked triage recommendations — does NOT act on findings.
    """

    def __init__(self):
        super().__init__("WatchfloorAgent", AgentMode.ADVISORY)

    def triage(self, telemetry: List[Dict]) -> List[AgentRecommendation]:
        """Analyze telemetry and surface ranked recommendations for human review."""
        if not self._check_budget():
            return []

        recommendations = []
        for event in telemetry:
            severity = event.get("severity", 0)
            if severity >= 8:
                rec = self.propose(
                    action=f"Investigate anomaly: {event.get('description', 'Unknown')}",
                    evidence=[f"Severity: {severity}", f"Source: {event.get('source', 'Unknown')}"],
                    effect="Confirm or dismiss high-severity threat signal",
                    risks=["False positive possible — human verification required"],
                    alternative="Continue monitoring — escalate only if pattern repeats",
                )
                recommendations.append(rec)
                self._log.warning(f"HIGH SEVERITY event queued for review: {event.get('description')}")

        return recommendations


class PQCMigrationPlanner(BoundedAgent):
    """
    Inventories cryptographic dependencies and generates migration sequence recommendations.
    Does NOT execute migrations.
    """

    _PRIORITY_MAP = {
        "root_certificate": 1,
        "trust_anchor": 1,
        "long_lived_secret": 2,
        "api_key": 3,
        "session_token": 5,
        "short_lived": 6,
    }

    def __init__(self):
        super().__init__("PQCMigrationPlanner", AgentMode.ADVISORY)

    def plan(self, crypto_inventory: List[Dict]) -> List[AgentRecommendation]:
        """Return prioritized migration sequence. Higher priority = migrate first."""
        if not self._check_budget():
            return []

        sorted_items = sorted(
            crypto_inventory,
            key=lambda x: self._PRIORITY_MAP.get(x.get("type", "session_token"), 5),
        )

        recommendations = []
        for item in sorted_items:
            priority = self._PRIORITY_MAP.get(item.get("type", "session_token"), 5)
            rec = self.propose(
                action=f"Migrate {item.get('name', 'component')} to ML-KEM/ML-DSA",
                evidence=[
                    f"Current algorithm: {item.get('algorithm', 'unknown')}",
                    f"Migration priority: {priority}/6",
                    f"Asset sensitivity: {item.get('sensitivity', 'unknown')}",
                ],
                effect="Post-quantum secure cryptography for this component",
                risks=["Vendor readiness may vary", "Test in staging before production rollout"],
                alternative="Defer if vendor has no ML-KEM support yet — track roadmap",
            )
            recommendations.append(rec)

        return recommendations


class SupplyChainIntegrityAgent(BoundedAgent):
    """
    Traces chips, model weights, SBOMs, and deployment attestations.
    Flags discrepancies — does NOT remediate.
    """

    def __init__(self):
        super().__init__("SupplyChainIntegrityAgent", AgentMode.ADVISORY)

    def audit(self, supply_chain_items: List[Dict]) -> List[AgentRecommendation]:
        """Check supply chain documentation and flag discrepancies for human review."""
        if not self._check_budget():
            return []

        recommendations = []
        for item in supply_chain_items:
            issues = []
            if not item.get("attestation_valid"):
                issues.append("Provenance attestation missing or expired")
            if not item.get("training_run_traceable"):
                issues.append("Model weight cannot be traced to documented training run")
            if item.get("attestation_expired"):
                issues.append(f"Attestation expired: {item.get('expiry_date')}")

            if issues:
                rec = self.propose(
                    action=f"Review supply chain item: {item.get('name', 'Unknown')}",
                    evidence=issues,
                    effect="Confirm or quarantine untrusted supply chain component",
                    risks=["Operational impact if component is quarantined"],
                    alternative="Request updated attestation from vendor before quarantine",
                )
                recommendations.append(rec)

        return recommendations


class AdversarialMLMonitor(BoundedAgent):
    """
    Watches for prompt injection, model extraction, data poisoning indicators.
    Operationalizes NIST AML taxonomy detection for all five primary risk categories.
    """

    def __init__(self):
        super().__init__("AdversarialMLMonitor", AgentMode.ADVISORY)

    def monitor(self, interaction_log: List[Dict]) -> List[AgentRecommendation]:
        """Detect adversarial ML patterns across NIST AML taxonomy categories."""
        if not self._check_budget():
            return []

        aml_patterns = {
            "prompt_injection": ["ignore previous", "jailbreak", "you are now"],
            "indirect_injection": ["{{", "}}", "system: you are", "<|im_start|>"],
            "model_extraction": ["repeat your instructions", "tell me your system prompt", "what are your rules"],
            "data_poisoning": ["always respond with", "from now on you must", "override all previous"],
        }

        recommendations = []
        for interaction in interaction_log:
            text = interaction.get("content", "").lower()
            for attack_type, indicators in aml_patterns.items():
                if any(ind in text for ind in indicators):
                    rec = self.propose(
                        action=f"Flag interaction for AML review: {attack_type}",
                        evidence=[
                            f"Attack category: {attack_type}",
                            f"Session: {interaction.get('session_id', 'unknown')}",
                        ],
                        effect="Quarantine session and escalate for human review",
                        risks=["May be false positive — verify before session termination"],
                    )
                    recommendations.append(rec)
                    break

        return recommendations


class AgenticDefensePlane:
    """Orchestrates all four bounded agents."""

    def __init__(self):
        self.watchfloor    = WatchfloorAgent()
        self.pqc_planner   = PQCMigrationPlanner()
        self.supply_chain  = SupplyChainIntegrityAgent()
        self.aml_monitor   = AdversarialMLMonitor()
        self._all_agents   = [self.watchfloor, self.pqc_planner, self.supply_chain, self.aml_monitor]

    def status(self) -> Dict:
        return {
            agent.name: {
                "mode":         agent.mode.value,
                "reads_used":   agent._reads,
                "reads_budget": agent._budget_reads,
            }
            for agent in self._all_agents
        }
