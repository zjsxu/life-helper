"""Tests for the emergency rule engine."""

import pytest
from pl_dss.rules import get_active_rules, RuleResult
from pl_dss.config import Config, ThresholdConfig, OverloadThresholds, RecoveryThresholds


@pytest.fixture
def sample_config():
    """Create a sample configuration for testing."""
    from pl_dss.config import AuthorityRules
    
    overload = OverloadThresholds(
        fixed_deadlines_14d=3,
        active_high_load_domains=3,
        avg_energy_score=2
    )
    recovery = RecoveryThresholds(
        fixed_deadlines_14d=1,
        active_high_load_domains=2,
        avg_energy_score=4
    )
    thresholds = ThresholdConfig(overload=overload, recovery=recovery)
    
    downgrade_rules = {
        "OVERLOADED": [
            "No new commitments",
            "Pause technical tool development",
            "Creative work reduced to minimum viable expression",
            "Administrative work: only non-delegable tasks"
        ],
        "STRESSED": [
            "Warning: approaching overload",
            "Discourage new projects",
            "Suggest creating time buffers"
        ]
    }
    
    recovery_advice = [
        "Deadlines have cleared",
        "High-load domains have reduced",
        "Energy levels have stabilized"
    ]
    
    authority_derivation = {
        "OVERLOADED": AuthorityRules(planning="DENIED", execution="DENIED", mode="CONTAINMENT"),
        "STRESSED": AuthorityRules(planning="DENIED", execution="DENIED", mode="CONTAINMENT"),
        "NORMAL": AuthorityRules(planning="ALLOWED", execution="DENIED", mode="NORMAL")
    }
    
    return Config(
        thresholds=thresholds,
        downgrade_rules=downgrade_rules,
        recovery_advice=recovery_advice,
        authority_derivation=authority_derivation
    )


def test_normal_state_returns_empty_rules(sample_config):
    """Test that NORMAL state returns no downgrade rules."""
    result = get_active_rules("NORMAL", sample_config)
    
    assert isinstance(result, RuleResult)
    assert result.state == "NORMAL"
    assert result.active_rules == []


def test_stressed_state_returns_stressed_rules(sample_config):
    """Test that STRESSED state returns configured STRESSED rules."""
    result = get_active_rules("STRESSED", sample_config)
    
    assert isinstance(result, RuleResult)
    assert result.state == "STRESSED"
    assert len(result.active_rules) == 3
    assert "Warning: approaching overload" in result.active_rules
    assert "Discourage new projects" in result.active_rules
    assert "Suggest creating time buffers" in result.active_rules


def test_overloaded_state_returns_overloaded_rules(sample_config):
    """Test that OVERLOADED state returns configured OVERLOADED rules."""
    result = get_active_rules("OVERLOADED", sample_config)
    
    assert isinstance(result, RuleResult)
    assert result.state == "OVERLOADED"
    assert len(result.active_rules) == 4
    assert "No new commitments" in result.active_rules
    assert "Pause technical tool development" in result.active_rules
    assert "Creative work reduced to minimum viable expression" in result.active_rules
    assert "Administrative work: only non-delegable tasks" in result.active_rules


def test_rules_returned_without_modification(sample_config):
    """Test that rules are returned exactly as configured."""
    result = get_active_rules("OVERLOADED", sample_config)
    
    # Rules should match exactly what's in the configuration
    expected_rules = sample_config.downgrade_rules["OVERLOADED"]
    assert result.active_rules == expected_rules
