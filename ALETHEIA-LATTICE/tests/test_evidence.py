"""Tests for Temporal Evidence Mesh — L2."""
import pytest
from aletheia_lattice.evidence.channels import (
    TemporalEvidenceMesh, EvidenceClaim, ChannelType, ConfidenceLevel
)

def _claim(channel=ChannelType.ARCHIVE, content="test"):
    return EvidenceClaim(
        content=content, channel=channel, source_id="test_src",
        source_reliability=0.9, collection_timestamp="2026-01-01",
        confidence=ConfidenceLevel.HIGH, temporal_scope="2026",
    )

def test_archive_ingest_retrieve():
    mesh = TemporalEvidenceMesh()
    mesh.ingest(_claim(content="FIPS 203 finalized 2024"))
    results = mesh.retrieve(ChannelType.ARCHIVE)
    assert len(results) == 1
    assert "FIPS" in results[0].content

def test_forecast_quarantine_blocks_without_optin():
    mesh = TemporalEvidenceMesh()
    mesh.ingest(_claim(ChannelType.FORECAST, "migration estimate 40-65%"))
    with pytest.raises(ValueError, match="include_forecast"):
        mesh.retrieve(ChannelType.FORECAST)

def test_forecast_accessible_with_optin():
    mesh = TemporalEvidenceMesh()
    mesh.ingest(_claim(ChannelType.FORECAST, "Scenario"))
    results = mesh.retrieve(ChannelType.FORECAST, include_forecast=True)
    assert len(results) == 1
    assert "FORECAST_CHANNEL_QUARANTINED" in results[0].policy_label

def test_channels_are_isolated():
    mesh = TemporalEvidenceMesh()
    mesh.ingest(_claim(ChannelType.ARCHIVE, "archive"))
    mesh.ingest(_claim(ChannelType.LIVE, "live"))
    mesh.ingest(_claim(ChannelType.FORECAST, "forecast"))
    s = mesh.stats()
    assert s["archive_count"] == 1
    assert s["live_count"] == 1
    assert s["forecast_count"] == 1

def test_promote_is_blocked():
    mesh = TemporalEvidenceMesh()
    fc = _claim(ChannelType.FORECAST, "scenario output")
    assert mesh.promote_is_blocked(fc) is True

def test_claim_format_output():
    c = _claim(content="FIPS 203 is finalized")
    out = c.format_output()
    assert "HIGH CONFIDENCE" in out
    assert "FIPS 203" in out
