# PQC Migration Integration Guide

## NIST Standards Baseline (FIPS 203/204/205)
- **FIPS 203 (ML-KEM)**: Key encapsulation — persistent storage and long-lived transport
- **FIPS 204 (ML-DSA)**: Digital signatures — model outputs, evidence ingestion, agent comms
- **FIPS 205 (SLH-DSA)**: Hash-based signatures — long-term artifact archival
- **HQC**: Selected March 2025, additional KEM for algorithm agility

## Migration Priority Order
1. Trust anchors (identity federation, root certificates)
2. Long-lived secrets (archive encryption, API keys at rest)
3. Artifact signing (model outputs, evidence ingestion events)
4. Agent-to-agent transport
5. Short-lived session tokens (lowest priority)

## Algorithm Agility Pattern
Design systems so algorithms are replaceable without architectural redesign:
```python
SIGNING_ALGORITHM = os.environ.get("SIGNING_ALG", "ML-DSA")  # swappable
KEY_ENCAP_ALGORITHM = os.environ.get("KEM_ALG", "ML-KEM")
```

## Integration with Aletheia Lattice
- `EvidenceClaim.policy_label` — tag claims with PQC readiness status
- `AgenticDefensePlane.pqc_planner` — inventories cryptographic dependencies
- All evidence ingestion events are signed (FIPS 204 target)
