# Why
Aletheia Lattice operationalizes NIST AI RMF 1.0, NIST Gen-AI Profile, FIPS 203/204/205, and CISA Secure-by-Design as concrete architectural controls. Every claim exits the system sourced, scored, temporally labeled, and cross-checked by an independent contradiction process.

# What
Five-layer Python architecture with FastAPI serving. Standards-aligned sovereign AI for national systems.
- `aletheia_lattice/ontology/` - L1 Ontology Core: typed directed knowledge graph, immutable append-only
- `aletheia_lattice/evidence/` - L2 Temporal Evidence Mesh: Archive + Live + Forecast channels (Forecast permanently quarantined)
- `aletheia_lattice/reasoning/` - L3 Parallel Reasoning Engine: 5 independent lanes, convergent promotion only
- `aletheia_lattice/agents/` - L4 Agentic Defense Plane: Watchfloor, PQC Planner, Supply Chain, AML Monitor
- `aletheia_lattice/immune/` - L5 Sovereign Immune Layer: VOID/TRACE/CAUTION/GRAVE/CONDEMNED gate states
- `aletheia_lattice/api/` - FastAPI server: POST /adjudicate, GET /health, GET /codex

# How
- Install: `pip install -e ".[dev]"`
- Test: `pytest tests/ -v --tb=short`
- Demo: `python scripts/demo.py`
- API: `uvicorn aletheia_lattice.api.server:app --port 8080`
- Lint: `ruff check aletheia_lattice/ tests/`

# Progressive Disclosure
Load skills only when performing the specific task.
- For commit formatting: Load `.claude/skills/git-commit.md`
- For build/test/verify: Load `.claude/skills/build-test-verify.md`
- For temporal separation architecture: Read `docs/agent-guides/temporal-separation.md`
- For the Sovereign Immune Layer: Read `docs/agent-guides/sovereign-immune-layer.md`
- For PQC migration integration: Read `docs/agent-guides/pqc-migration.md`
