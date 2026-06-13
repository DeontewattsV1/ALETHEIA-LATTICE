---
name: build-test-verify
description: Build, test, and verify workflow for Aletheia Lattice.
---

## Setup
```bash
pip install -e ".[dev]"
```

## Test
```bash
pytest tests/ -v --tb=short
pytest tests/test_evidence.py -v         # evidence channel isolation
pytest tests/test_immune.py -v           # sovereign immune layer
pytest tests/test_reasoning.py -v        # parallel reasoning engine
```

## Lint
```bash
ruff check aletheia_lattice/ tests/
```

## Demo
```bash
python scripts/demo.py
```

## Key invariants — never break these
- Forecast channel content CANNOT be promoted to Archive or Live channels under any condition
- Every claim exiting the system must carry: source_id, confidence, temporal_scope, policy_label
- No consequential agent action executes without explicit human approval gate
- SovereignImmuneLayer intercepts at EVERY boundary — prompt, retrieval, tool, egress, post-action
