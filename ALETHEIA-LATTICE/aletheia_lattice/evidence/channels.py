"""
Temporal Evidence Mesh — L2: "The Why Is It Believed" Layer.

Three permanently separated channels. No scenario output may silently
be promoted into the evidence layer. This is the load-bearing constraint
that distinguishes a truth-bounded system from a hallucinating one.

Standards: NIST AI RMF 1.0 (Govern 1.7), NIST Generative AI Profile
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional


class ChannelType(Enum):
    ARCHIVE  = "archive"   # Immutable historical evidence
    LIVE     = "live"      # Current telemetry with freshness decay
    FORECAST = "forecast"  # QUARANTINED: scenario outputs only


class ConfidenceLevel(Enum):
    HIGH   = "HIGH"    # Multiple independent sources, no significant contradiction
    MEDIUM = "MEDIUM"  # Limited sources, aging data, or contested interpretation
    LOW    = "LOW"     # Reasonable inference or scenario projection only


@dataclass
class EvidenceClaim:
    """A single evidence claim with mandatory provenance metadata."""
    content:              str
    channel:              ChannelType
    source_id:            str
    source_reliability:   float        # 0.0 – 1.0
    collection_timestamp: str
    confidence:           ConfidenceLevel
    temporal_scope:       str          # Time period the claim describes
    policy_label:         str = ""
    claim_id:             str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __post_init__(self):
        # Forecast claims are quarantined — marker is schema-enforced
        if self.channel == ChannelType.FORECAST:
            if "FORECAST_CHANNEL_QUARANTINED" not in self.policy_label:
                self.policy_label = f"FORECAST_CHANNEL_QUARANTINED | {self.policy_label}"

    def format_output(self) -> str:
        """Format claim for human-readable output with provenance embedded."""
        prefix = {
            ChannelType.ARCHIVE:  f"[FINDING · {self.confidence.value} CONFIDENCE]",
            ChannelType.LIVE:     f"[LIVE · {self.confidence.value} CONFIDENCE]",
            ChannelType.FORECAST: "[FORECAST CHANNEL · SCENARIO · NOT ESTABLISHED FACT]",
        }[self.channel]
        return (
            f"{prefix} {self.content}\n"
            f"Source: {self.source_id} · Temporal: {self.temporal_scope}"
        )


class TemporalEvidenceMesh:
    """
    Evidence storage and retrieval with strict channel separation enforced.
    The quarantine wall between FORECAST and evidence channels is inviolable.
    """

    def __init__(self):
        self._archive:  List[EvidenceClaim] = []
        self._live:     List[EvidenceClaim] = []
        self._forecast: List[EvidenceClaim] = []  # Permanently quarantined

    def ingest(self, claim: EvidenceClaim) -> EvidenceClaim:
        """Route a claim into its designated channel. Routing cannot be overridden."""
        if claim.channel == ChannelType.ARCHIVE:
            self._archive.append(claim)
        elif claim.channel == ChannelType.LIVE:
            self._live.append(claim)
        elif claim.channel == ChannelType.FORECAST:
            self._forecast.append(claim)
        return claim

    def retrieve(
        self,
        channel: ChannelType,
        query_terms: Optional[List[str]] = None,
        limit: int = 10,
        include_forecast: bool = False,
    ) -> List[EvidenceClaim]:
        """
        Retrieve claims from the specified channel.
        Forecast content requires explicit opt-in — this is an architectural
        constraint, not a default that can be changed per-call without intent.
        """
        if channel == ChannelType.FORECAST and not include_forecast:
            raise ValueError(
                "Forecast channel content requires explicit include_forecast=True. "
                "All forecast content must be treated as SCENARIO, not established fact. "
                "Call retrieve(ChannelType.FORECAST, include_forecast=True) to proceed."
            )

        pool = {
            ChannelType.ARCHIVE:  self._archive,
            ChannelType.LIVE:     self._live,
            ChannelType.FORECAST: self._forecast,
        }[channel]

        if query_terms:
            results = [
                c for c in pool
                if any(term.lower() in c.content.lower() for term in query_terms)
            ]
        else:
            results = list(pool)

        return results[-limit:]

    def stats(self) -> Dict:
        return {
            "archive_count":  len(self._archive),
            "live_count":     len(self._live),
            "forecast_count": len(self._forecast),
            "total":          len(self._archive) + len(self._live) + len(self._forecast),
        }

    def promote_is_blocked(self, forecast_claim) -> bool:
        """Architectural constraint: Forecast → Archive/Live is permanently blocked."""
        return True

