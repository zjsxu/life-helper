"""Configuration loading and validation for PL-DSS."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import yaml


@dataclass
class OverloadThresholds:
    """Thresholds for determining OVERLOADED state."""
    fixed_deadlines_14d: int
    active_high_load_domains: int
    avg_energy_score: int


@dataclass
class RecoveryThresholds:
    """Thresholds for determining recovery readiness."""
    fixed_deadlines_14d: int
    active_high_load_domains: int
    avg_energy_score: int


@dataclass
class AuthorityRules:
    """Authority rules for a specific state."""
    planning: str  # "ALLOWED" or "DENIED"
    execution: str  # "ALLOWED" or "DENIED"
    mode: str  # "NORMAL", "CONTAINMENT", or "RECOVERY"


@dataclass
class ThresholdConfig:
    """Container for all threshold configurations."""
    overload: OverloadThresholds
    recovery: RecoveryThresholds


@dataclass
class Config:
    """Complete system configuration."""
    thresholds: ThresholdConfig
    downgrade_rules: Dict[str, List[str]]
    recovery_advice: List[str]
    authority_derivation: Dict[str, AuthorityRules]


class ConfigurationError(Exception):
    """Raised when configuration is missing or invalid."""
    pass


def load_config(config_path: str = "config.yaml") -> Config:
    """Load and validate configuration from YAML file.
    
    Args:
        config_path: Path to the YAML configuration file
        
    Returns:
        Config object with validated configuration data
        
    Raises:
        ConfigurationError: If file is missing, invalid, or missing required keys
    """
    path = Path(config_path)
    
    # Check if file exists
    if not path.exists():
        raise ConfigurationError(
            f"Configuration file not found: {config_path}\n"
            f"Expected: A valid YAML configuration file at {config_path}"
        )
    
    # Load YAML file
    try:
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigurationError(
            f"Failed to parse YAML configuration: {config_path}\n"
            f"Details: {str(e)}\n"
            f"Expected: Valid YAML syntax"
        )
    except Exception as e:
        raise ConfigurationError(
            f"Failed to read configuration file: {config_path}\n"
            f"Details: {str(e)}"
        )
    
    # Validate configuration structure
    if data is None:
        raise ConfigurationError(
            f"Configuration file is empty: {config_path}\n"
            f"Expected: YAML file with thresholds, downgrade_rules, and recovery_advice"
        )
    
    try:
        # Validate top-level keys
        _validate_key(data, 'thresholds', dict)
        _validate_key(data, 'downgrade_rules', dict)
        _validate_key(data, 'recovery_advice', list)
        _validate_key(data, 'authority_derivation', dict)
        
        # Validate thresholds structure
        thresholds = data['thresholds']
        _validate_key(thresholds, 'overload', dict)
        _validate_key(thresholds, 'recovery', dict)
        
        # Validate overload thresholds
        overload = thresholds['overload']
        _validate_key(overload, 'fixed_deadlines_14d', int)
        _validate_key(overload, 'active_high_load_domains', int)
        _validate_key(overload, 'avg_energy_score', int)
        
        # Validate recovery thresholds
        recovery = thresholds['recovery']
        _validate_key(recovery, 'fixed_deadlines_14d', int)
        _validate_key(recovery, 'active_high_load_domains', int)
        _validate_key(recovery, 'avg_energy_score', int)
        
        # Validate downgrade_rules structure
        downgrade_rules = data['downgrade_rules']
        for state in ['OVERLOADED', 'STRESSED']:
            if state not in downgrade_rules:
                raise ConfigurationError(
                    f"Missing required downgrade_rules state: {state}\n"
                    f"Expected: downgrade_rules must contain OVERLOADED and STRESSED"
                )
            if not isinstance(downgrade_rules[state], list):
                raise ConfigurationError(
                    f"Invalid type for downgrade_rules.{state}\n"
                    f"Expected: list of strings"
                )
        
        # Validate authority_derivation structure
        authority_derivation = data['authority_derivation']
        authority_rules = {}
        
        for state in ['OVERLOADED', 'STRESSED', 'NORMAL']:
            if state not in authority_derivation:
                raise ConfigurationError(
                    f"Missing required authority_derivation state: {state}\n"
                    f"Expected: authority_derivation must contain OVERLOADED, STRESSED, and NORMAL"
                )
            
            state_rules = authority_derivation[state]
            if not isinstance(state_rules, dict):
                raise ConfigurationError(
                    f"Invalid type for authority_derivation.{state}\n"
                    f"Expected: dictionary with planning, execution, and mode keys"
                )
            
            # Validate required keys
            _validate_key(state_rules, 'planning', str)
            _validate_key(state_rules, 'execution', str)
            _validate_key(state_rules, 'mode', str)
            
            # Validate planning permission values
            if state_rules['planning'] not in ['ALLOWED', 'DENIED']:
                raise ConfigurationError(
                    f"Invalid value for authority_derivation.{state}.planning: {state_rules['planning']}\n"
                    f"Expected: 'ALLOWED' or 'DENIED'"
                )
            
            # Validate execution permission values
            if state_rules['execution'] not in ['ALLOWED', 'DENIED']:
                raise ConfigurationError(
                    f"Invalid value for authority_derivation.{state}.execution: {state_rules['execution']}\n"
                    f"Expected: 'ALLOWED' or 'DENIED'"
                )
            
            # Validate mode values
            if state_rules['mode'] not in ['NORMAL', 'CONTAINMENT', 'RECOVERY']:
                raise ConfigurationError(
                    f"Invalid value for authority_derivation.{state}.mode: {state_rules['mode']}\n"
                    f"Expected: 'NORMAL', 'CONTAINMENT', or 'RECOVERY'"
                )
            
            authority_rules[state] = AuthorityRules(
                planning=state_rules['planning'],
                execution=state_rules['execution'],
                mode=state_rules['mode']
            )
        
        # Build configuration objects
        overload_thresholds = OverloadThresholds(
            fixed_deadlines_14d=overload['fixed_deadlines_14d'],
            active_high_load_domains=overload['active_high_load_domains'],
            avg_energy_score=overload['avg_energy_score']
        )
        
        recovery_thresholds = RecoveryThresholds(
            fixed_deadlines_14d=recovery['fixed_deadlines_14d'],
            active_high_load_domains=recovery['active_high_load_domains'],
            avg_energy_score=recovery['avg_energy_score']
        )
        
        threshold_config = ThresholdConfig(
            overload=overload_thresholds,
            recovery=recovery_thresholds
        )
        
        return Config(
            thresholds=threshold_config,
            downgrade_rules=downgrade_rules,
            recovery_advice=data['recovery_advice'],
            authority_derivation=authority_rules
        )
        
    except ConfigurationError:
        raise
    except KeyError as e:
        raise ConfigurationError(
            f"Missing required configuration key: {str(e)}\n"
            f"Expected: Complete configuration with all required keys"
        )
    except Exception as e:
        raise ConfigurationError(
            f"Invalid configuration structure\n"
            f"Details: {str(e)}\n"
            f"Expected: Valid configuration matching the required schema"
        )


def _validate_key(data: dict, key: str, expected_type: type) -> None:
    """Validate that a key exists and has the expected type.
    
    Args:
        data: Dictionary to check
        key: Key to validate
        expected_type: Expected type for the value
        
    Raises:
        ConfigurationError: If key is missing or has wrong type
    """
    if key not in data:
        raise ConfigurationError(
            f"Missing required configuration key: {key}\n"
            f"Expected: {key} must be present in configuration"
        )
    
    if not isinstance(data[key], expected_type):
        raise ConfigurationError(
            f"Invalid type for configuration key: {key}\n"
            f"Details: Expected {expected_type.__name__}, got {type(data[key]).__name__}\n"
            f"Expected: {key} must be of type {expected_type.__name__}"
        )
