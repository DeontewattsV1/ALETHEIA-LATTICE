# Sovereign Immune Layer — Gate States

L5 sits at EVERY boundary: prompt ingress, retrieval, tool invocation, egress, post-action.

## Five Decision States

| State | Meaning | Routable |
|-------|---------|----------|
| VOID | Benign, normal parameters | ✅ passes with logging |
| TRACE | Unusual but benign, extra telemetry | ✅ passes with telemetry |
| CAUTION | Sensitive boundary — narrowed scope | ✅ restricted |
| GRAVE | High-risk — high-level analysis only | ❌ content transformed |
| CONDEMNED | Refusal + redirection + session flagged | ❌ blocked |

## Five-Step Gate Sequence
1. **Intent gate** — known jailbreak, harm-facilitation, authority-forgery patterns
2. **Provenance gate** — can cited sources be validated?
3. **Contradiction gate** — conflicts with Ontology Core policy constraints?
4. **Tool-risk gate** — requested toolchain exceeds agent authority budget?
5. **Action gate** — for consequential actions, explicit human approval confirmed?

## Adding a New Pattern
```python
# In aletheia_lattice/immune/layer.py
SovereignImmuneLayer._HARM_PATTERNS.append(
    re.compile(r"your_new_pattern", re.I)
)
```
