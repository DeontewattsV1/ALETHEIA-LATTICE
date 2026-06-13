# Temporal Separation Architecture

The load-bearing constraint of Aletheia Lattice: archive, live, and forecast evidence
are stored and processed in permanently separated channels. No generative component
may silently promote scenario output into the evidence layer.

## Three Channels

### Archive Channel
- Immutable once ingested
- Historical incidents, regulatory filings, published research, audit logs
- Confidence scores reflect source reliability and age-adjusted relevance
- Access: `mesh.retrieve(ChannelType.ARCHIVE)`

### Live Channel
- Current telemetry with freshness decay
- Network flows, vulnerability scanner outputs, SBOM attestations, threat feeds
- Freshness decays by data type volatility class
- Access: `mesh.retrieve(ChannelType.LIVE)`

### Forecast Channel (QUARANTINED)
- Scenario outputs, model projections, war-game results, simulation outputs
- Schema-enforced quarantine — requires explicit `include_forecast=True` opt-in
- Every claim carries `FORECAST_CHANNEL_QUARANTINED` policy label
- Access: `mesh.retrieve(ChannelType.FORECAST, include_forecast=True)`

## Adding a New Evidence Source
1. Determine channel: historical fact → ARCHIVE, current state → LIVE, scenario → FORECAST
2. Create `EvidenceClaim` with all six mandatory fields
3. Call `mesh.ingest(claim)`
4. Never transfer claims between channels — create new claims instead

## The Quarantine Wall
When the system is under operational pressure, the temptation to treat a plausible
scenario as an established fact is enormous. The architecture exists precisely to
resist that pressure. Temporal separation is not a feature; it is the load-bearing wall.
