"""
Ontology Core — L1: The "What Is" Layer.

Machine-readable typed knowledge graph. Not a vector store, not a chatbot memory.
Every node carries provenance; every edge carries a confidence score.
The graph is immutable by design — new evidence appends, never overwrites.
"""

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Tuple

_log = logging.getLogger("aletheia.ontology")


class NodeType(Enum):
    ENTITY       = "entity"      # systems, organizations, actors
    LAW          = "law"         # regulatory constraints, physical laws
    CRYPTO_STATE = "crypto_state" # cryptographic algorithm status
    POLICY       = "policy"      # governance rules, mission constraints
    DEPENDENCY   = "dependency"  # software/hardware dependency records
    CONCEPT      = "concept"     # abstract definitional nodes


class EdgeType(Enum):
    DEPENDS_ON   = "depends-on"
    GOVERNS      = "governs"
    CONTRADICTS  = "contradicts"
    SUPERSEDES   = "supersedes"
    DERIVES_FROM = "derives-from"
    IS_INSTANCE  = "is-instance-of"
    VULNERABLE_TO = "vulnerable-to"


class DerivationMethod(Enum):
    ASSERTED = "asserted"   # explicitly stated by authority source
    INFERRED = "inferred"   # derived from other nodes
    MEASURED = "measured"   # empirically observed


@dataclass(frozen=True)
class OntologyNode:
    """Immutable node in the knowledge graph."""
    node_id:          str
    node_type:        NodeType
    label:            str
    description:      str
    authority_source: str
    schema_version:   str = "1.0"
    namespace:        str = "aletheia"
    created_at:       str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def fingerprint(self) -> str:
        raw = f"{self.namespace}:{self.node_id}:{self.label}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


@dataclass(frozen=True)
class OntologyEdge:
    """Typed, scored relationship between two nodes."""
    source_id:        str
    target_id:        str
    edge_type:        EdgeType
    confidence:       float          # 0.0 – 1.0
    derivation:       DerivationMethod
    policy_label:     str = ""
    created_at:       str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class OntologyCore:
    """
    Typed, directed knowledge graph — the system's single source of structured truth.

    Immutable append-only design: full belief revision history is always recoverable.
    New evidence creates new nodes/edges rather than overwriting existing ones.
    """

    def __init__(self):
        self._nodes: Dict[str, List[OntologyNode]] = {}   # node_id → version history
        self._edges: List[OntologyEdge] = []
        self._bootstrap()

    def _bootstrap(self):
        """Seed with foundational cryptographic and policy facts."""
        seed_nodes = [
            OntologyNode(
                node_id="fips-203", node_type=NodeType.CRYPTO_STATE,
                label="FIPS 203 (ML-KEM)",
                description="NIST post-quantum key encapsulation standard. Finalized August 13, 2024.",
                authority_source="NIST PQC Project",
            ),
            OntologyNode(
                node_id="fips-204", node_type=NodeType.CRYPTO_STATE,
                label="FIPS 204 (ML-DSA)",
                description="NIST post-quantum digital signature standard. Finalized August 13, 2024.",
                authority_source="NIST PQC Project",
            ),
            OntologyNode(
                node_id="fips-205", node_type=NodeType.CRYPTO_STATE,
                label="FIPS 205 (SLH-DSA)",
                description="Hash-based signature standard for long-term archival. Finalized August 13, 2024.",
                authority_source="NIST PQC Project",
            ),
            OntologyNode(
                node_id="rsa-2048", node_type=NodeType.CRYPTO_STATE,
                label="RSA-2048",
                description="Classical RSA — vulnerable to Shor's algorithm on a sufficiently large quantum processor.",
                authority_source="NIST SP 800-131A",
            ),
            OntologyNode(
                node_id="nist-ai-rmf", node_type=NodeType.LAW,
                label="NIST AI RMF 1.0",
                description="NIST AI Risk Management Framework. Defines trustworthy AI properties: valid, safe, secure, explainable, privacy-enhanced, bias-managed.",
                authority_source="NIST AI RMF 1.0 (Jan 2023)",
            ),
        ]
        for node in seed_nodes:
            self.add_node(node)

        # Seed edges
        self.add_edge(OntologyEdge(
            source_id="fips-203", target_id="rsa-2048",
            edge_type=EdgeType.SUPERSEDES,
            confidence=0.95,
            derivation=DerivationMethod.ASSERTED,
            policy_label="PQC_MIGRATION",
        ))

    def add_node(self, node: OntologyNode) -> OntologyNode:
        """Append a node. Existing versions are preserved (immutable)."""
        if node.node_id not in self._nodes:
            self._nodes[node.node_id] = []
        self._nodes[node.node_id].append(node)
        _log.debug(f"Node added: {node.node_id} v{len(self._nodes[node.node_id])}")
        return node

    def add_edge(self, edge: OntologyEdge) -> OntologyEdge:
        """Add a typed relationship between two nodes."""
        self._edges.append(edge)
        return edge

    def get_node(self, node_id: str) -> Optional[OntologyNode]:
        """Return the most recent version of a node."""
        versions = self._nodes.get(node_id)
        return versions[-1] if versions else None

    def get_node_history(self, node_id: str) -> List[OntologyNode]:
        """Return full version history (belief revision record)."""
        return list(self._nodes.get(node_id, []))

    def get_edges(self, source_id: str, edge_type: Optional[EdgeType] = None) -> List[OntologyEdge]:
        return [
            e for e in self._edges
            if e.source_id == source_id
            and (edge_type is None or e.edge_type == edge_type)
        ]

    def check_consistency(self, node_id: str, claim: str) -> Tuple[bool, str]:
        """
        Check if a new claim is consistent with existing nodes.
        Returns (is_consistent, explanation).
        """
        node = self.get_node(node_id)
        if node is None:
            return True, "No existing node — claim is new."
        # Simple contradiction check: look for CONTRADICTS edges
        contradicting = self.get_edges(node_id, EdgeType.CONTRADICTS)
        if contradicting:
            return False, f"Node {node_id} has {len(contradicting)} known contradictions."
        return True, "Consistent with existing ontology."

    def stats(self) -> Dict:
        return {
            "unique_nodes":   len(self._nodes),
            "total_versions": sum(len(v) for v in self._nodes.values()),
            "total_edges":    len(self._edges),
        }
