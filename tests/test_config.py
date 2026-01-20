"""Unit tests for configuration loading and validation.

Tests cover:
- Loading valid configuration with authority_derivation
- Missing authority_derivation section
- Invalid authority values
- Requirements: 7.1, 7.2, 7.4
"""

import pytest
import tempfile
from pathlib import Path
from pl_dss.config import (
    load_config,
    Config,
    ConfigurationError,
    ThresholdConfig,
    OverloadThresholds,
    RecoveryThresholds,
    AuthorityRules
)


# Test 1: Load valid configuration with authority_derivation
def test_load_valid_configuration_with_authority_derivation(tmp_path):
    """Test loading a valid configuration file with authority_derivation section.
    
    Requirements: 7.1, 7.2
    """
    # Create a valid configuration file
    config_content = """
thresholds:
  overload:
    fixed_deadlines_14d: 3
    active_high_load_domains: 3
    avg_energy_score: 2
  recovery:
    fixed_deadlines_14d: 1
    active_high_load_domains: 2
    avg_energy_score: 4

downgrade_rules:
  OVERLOADED:
    - "No new commitments"
    - "Pause technical tool development"
  STRESSED:
    - "Warning: approaching overload"
    - "Discourage new projects"

recovery_advice:
  - "Deadlines have cleared"
  - "High-load domains have reduced"

authority_derivation:
  OVERLOADED:
    planning: DENIED
    execution: DENIED
    mode: CONTAINMENT
  STRESSED:
    planning: DENIED
    execution: DENIED
    mode: CONTAINMENT
  NORMAL:
    planning: ALLOWED
    execution: DENIED
    mode: NORMAL
"""
    
    config_file = tmp_path / "test_config.yaml"
    config_file.write_text(config_content)
    
    # Load configuration
    config = load_config(str(config_file))
    
    # Verify configuration structure
    assert isinstance(config, Config)
    assert isinstance(config.thresholds, ThresholdConfig)
    assert isinstance(config.thresholds.overload, OverloadThresholds)
    assert isinstance(config.thresholds.recovery, RecoveryThresholds)
    
    # Verify threshold values
    assert config.thresholds.overload.fixed_deadlines_14d == 3
    assert config.thresholds.overload.active_high_load_domains == 3
    assert config.thresholds.overload.avg_energy_score == 2
    assert config.thresholds.recovery.fixed_deadlines_14d == 1
    assert config.thresholds.recovery.active_high_load_domains == 2
    assert config.thresholds.recovery.avg_energy_score == 4
    
    # Verify downgrade rules
    assert "OVERLOADED" in config.downgrade_rules
    assert "STRESSED" in config.downgrade_rules
    assert len(config.downgrade_rules["OVERLOADED"]) == 2
    assert len(config.downgrade_rules["STRESSED"]) == 2
    
    # Verify recovery advice
    assert len(config.recovery_advice) == 2
    
    # Verify authority_derivation
    assert isinstance(config.authority_derivation, dict)
    assert "OVERLOADED" in config.authority_derivation
    assert "STRESSED" in config.authority_derivation
    assert "NORMAL" in config.authority_derivation
    
    # Verify OVERLOADED authority rules
    overloaded_rules = config.authority_derivation["OVERLOADED"]
    assert isinstance(overloaded_rules, AuthorityRules)
    assert overloaded_rules.planning == "DENIED"
    assert overloaded_rules.execution == "DENIED"
    assert overloaded_rules.mode == "CONTAINMENT"
    
    # Verify STRESSED authority rules
    stressed_rules = config.authority_derivation["STRESSED"]
    assert isinstance(stressed_rules, AuthorityRules)
    assert stressed_rules.planning == "DENIED"
    assert stressed_rules.execution == "DENIED"
    assert stressed_rules.mode == "CONTAINMENT"
    
    # Verify NORMAL authority rules
    normal_rules = config.authority_derivation["NORMAL"]
    assert isinstance(normal_rules, AuthorityRules)
    assert normal_rules.planning == "ALLOWED"
    assert normal_rules.execution == "DENIED"
    assert normal_rules.mode == "NORMAL"


# Test 2: Missing authority_derivation section
def test_missing_authority_derivation_section(tmp_path):
    """Test that missing authority_derivation section raises ConfigurationError.
    
    Requirements: 7.4
    """
    # Create configuration without authority_derivation
    config_content = """
thresholds:
  overload:
    fixed_deadlines_14d: 3
    active_high_load_domains: 3
    avg_energy_score: 2
  recovery:
    fixed_deadlines_14d: 1
    active_high_load_domains: 2
    avg_energy_score: 4

downgrade_rules:
  OVERLOADED:
    - "No new commitments"
  STRESSED:
    - "Warning: approaching overload"

recovery_advice:
  - "Deadlines have cleared"
"""
    
    config_file = tmp_path / "test_config_no_authority.yaml"
    config_file.write_text(config_content)
    
    # Attempt to load configuration
    with pytest.raises(ConfigurationError) as exc_info:
        load_config(str(config_file))
    
    # Verify error message mentions missing authority_derivation
    error_message = str(exc_info.value)
    assert "authority_derivation" in error_message.lower()


# Test 3: Invalid authority values - invalid planning permission
def test_invalid_planning_permission_value(tmp_path):
    """Test that invalid planning permission value raises ConfigurationError.
    
    Requirements: 7.4
    """
    # Create configuration with invalid planning value
    config_content = """
thresholds:
  overload:
    fixed_deadlines_14d: 3
    active_high_load_domains: 3
    avg_energy_score: 2
  recovery:
    fixed_deadlines_14d: 1
    active_high_load_domains: 2
    avg_energy_score: 4

downgrade_rules:
  OVERLOADED:
    - "No new commitments"
  STRESSED:
    - "Warning: approaching overload"

recovery_advice:
  - "Deadlines have cleared"

authority_derivation:
  OVERLOADED:
    planning: INVALID_VALUE
    execution: DENIED
    mode: CONTAINMENT
  STRESSED:
    planning: DENIED
    execution: DENIED
    mode: CONTAINMENT
  NORMAL:
    planning: ALLOWED
    execution: DENIED
    mode: NORMAL
"""
    
    config_file = tmp_path / "test_config_invalid_planning.yaml"
    config_file.write_text(config_content)
    
    # Attempt to load configuration
    with pytest.raises(ConfigurationError) as exc_info:
        load_config(str(config_file))
    
    # Verify error message mentions invalid planning value
    error_message = str(exc_info.value)
    assert "planning" in error_message.lower()
    assert "ALLOWED" in error_message or "DENIED" in error_message


# Test 4: Invalid authority values - invalid execution permission
def test_invalid_execution_permission_value(tmp_path):
    """Test that invalid execution permission value raises ConfigurationError.
    
    Requirements: 7.4
    """
    # Create configuration with invalid execution value
    config_content = """
thresholds:
  overload:
    fixed_deadlines_14d: 3
    active_high_load_domains: 3
    avg_energy_score: 2
  recovery:
    fixed_deadlines_14d: 1
    active_high_load_domains: 2
    avg_energy_score: 4

downgrade_rules:
  OVERLOADED:
    - "No new commitments"
  STRESSED:
    - "Warning: approaching overload"

recovery_advice:
  - "Deadlines have cleared"

authority_derivation:
  OVERLOADED:
    planning: DENIED
    execution: MAYBE
    mode: CONTAINMENT
  STRESSED:
    planning: DENIED
    execution: DENIED
    mode: CONTAINMENT
  NORMAL:
    planning: ALLOWED
    execution: DENIED
    mode: NORMAL
"""
    
    config_file = tmp_path / "test_config_invalid_execution.yaml"
    config_file.write_text(config_content)
    
    # Attempt to load configuration
    with pytest.raises(ConfigurationError) as exc_info:
        load_config(str(config_file))
    
    # Verify error message mentions invalid execution value
    error_message = str(exc_info.value)
    assert "execution" in error_message.lower()
    assert "ALLOWED" in error_message or "DENIED" in error_message


# Test 5: Invalid authority values - invalid mode
def test_invalid_mode_value(tmp_path):
    """Test that invalid mode value raises ConfigurationError.
    
    Requirements: 7.4
    """
    # Create configuration with invalid mode value
    config_content = """
thresholds:
  overload:
    fixed_deadlines_14d: 3
    active_high_load_domains: 3
    avg_energy_score: 2
  recovery:
    fixed_deadlines_14d: 1
    active_high_load_domains: 2
    avg_energy_score: 4

downgrade_rules:
  OVERLOADED:
    - "No new commitments"
  STRESSED:
    - "Warning: approaching overload"

recovery_advice:
  - "Deadlines have cleared"

authority_derivation:
  OVERLOADED:
    planning: DENIED
    execution: DENIED
    mode: PANIC
  STRESSED:
    planning: DENIED
    execution: DENIED
    mode: CONTAINMENT
  NORMAL:
    planning: ALLOWED
    execution: DENIED
    mode: NORMAL
"""
    
    config_file = tmp_path / "test_config_invalid_mode.yaml"
    config_file.write_text(config_content)
    
    # Attempt to load configuration
    with pytest.raises(ConfigurationError) as exc_info:
        load_config(str(config_file))
    
    # Verify error message mentions invalid mode value
    error_message = str(exc_info.value)
    assert "mode" in error_message.lower()
    assert "NORMAL" in error_message or "CONTAINMENT" in error_message or "RECOVERY" in error_message


# Test 6: Missing state in authority_derivation
def test_missing_state_in_authority_derivation(tmp_path):
    """Test that missing state in authority_derivation raises ConfigurationError.
    
    Requirements: 7.4
    """
    # Create configuration missing NORMAL state
    config_content = """
thresholds:
  overload:
    fixed_deadlines_14d: 3
    active_high_load_domains: 3
    avg_energy_score: 2
  recovery:
    fixed_deadlines_14d: 1
    active_high_load_domains: 2
    avg_energy_score: 4

downgrade_rules:
  OVERLOADED:
    - "No new commitments"
  STRESSED:
    - "Warning: approaching overload"

recovery_advice:
  - "Deadlines have cleared"

authority_derivation:
  OVERLOADED:
    planning: DENIED
    execution: DENIED
    mode: CONTAINMENT
  STRESSED:
    planning: DENIED
    execution: DENIED
    mode: CONTAINMENT
"""
    
    config_file = tmp_path / "test_config_missing_state.yaml"
    config_file.write_text(config_content)
    
    # Attempt to load configuration
    with pytest.raises(ConfigurationError) as exc_info:
        load_config(str(config_file))
    
    # Verify error message mentions missing state
    error_message = str(exc_info.value)
    assert "NORMAL" in error_message or "state" in error_message.lower()


# Test 7: Missing required key in authority state
def test_missing_required_key_in_authority_state(tmp_path):
    """Test that missing required key in authority state raises ConfigurationError.
    
    Requirements: 7.4
    """
    # Create configuration with missing 'mode' key
    config_content = """
thresholds:
  overload:
    fixed_deadlines_14d: 3
    active_high_load_domains: 3
    avg_energy_score: 2
  recovery:
    fixed_deadlines_14d: 1
    active_high_load_domains: 2
    avg_energy_score: 4

downgrade_rules:
  OVERLOADED:
    - "No new commitments"
  STRESSED:
    - "Warning: approaching overload"

recovery_advice:
  - "Deadlines have cleared"

authority_derivation:
  OVERLOADED:
    planning: DENIED
    execution: DENIED
  STRESSED:
    planning: DENIED
    execution: DENIED
    mode: CONTAINMENT
  NORMAL:
    planning: ALLOWED
    execution: DENIED
    mode: NORMAL
"""
    
    config_file = tmp_path / "test_config_missing_key.yaml"
    config_file.write_text(config_content)
    
    # Attempt to load configuration
    with pytest.raises(ConfigurationError) as exc_info:
        load_config(str(config_file))
    
    # Verify error message mentions missing key
    error_message = str(exc_info.value)
    assert "mode" in error_message.lower() or "missing" in error_message.lower()


# Test 8: Load actual config.yaml file
def test_load_actual_config_file():
    """Test loading the actual config.yaml file from the project.
    
    Requirements: 7.1, 7.2
    """
    # Load the actual configuration file
    config = load_config("config.yaml")
    
    # Verify it loads successfully
    assert isinstance(config, Config)
    assert isinstance(config.authority_derivation, dict)
    
    # Verify all required states are present
    assert "OVERLOADED" in config.authority_derivation
    assert "STRESSED" in config.authority_derivation
    assert "NORMAL" in config.authority_derivation
    
    # Verify authority rules are properly structured
    for state in ["OVERLOADED", "STRESSED", "NORMAL"]:
        rules = config.authority_derivation[state]
        assert isinstance(rules, AuthorityRules)
        assert rules.planning in ["ALLOWED", "DENIED"]
        assert rules.execution in ["ALLOWED", "DENIED"]
        assert rules.mode in ["NORMAL", "CONTAINMENT", "RECOVERY"]
