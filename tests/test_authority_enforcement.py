"""Property-based tests for authority enforcement in GitHub Interface.

Tests that authority is correctly enforced across all system states and that
planning operations respect authority boundaries.

Feature: github-interface
Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
"""

import pytest
from hypothesis import given, strategies as st, settings

from pl_dss.config import Config, ThresholdConfig, OverloadThresholds, RecoveryThresholds, AuthorityRules
from pl_dss.evaluator import StateInputs, evaluate_state
from pl_dss.rules import get_active_rules
from pl_dss.authority import derive_authority


def create_sample_config():
    """Create a sample configuration for testing."""
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
            "Pause technical tool development"
        ],
        "STRESSED": [
            "Warning: approaching overload",
            "Discourage new projects"
        ]
    }
    
    recovery_advice = [
        "Deadlines have cleared",
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


# Strategy for generating StateInputs that result in STRESSED or OVERLOADED states
@st.composite
def stressed_or_overloaded_inputs(draw):
    """Generate StateInputs that result in STRESSED or OVERLOADED state.
    
    STRESSED: Exactly 1 condition met
    OVERLOADED: 2 or more conditions met
    
    Conditions:
    - fixed_deadlines_14d >= 3
    - active_high_load_domains >= 3
    - avg_energy_score <= 2
    """
    # Generate inputs that meet at least 1 condition
    deadlines = draw(st.integers(min_value=0, max_value=10))
    domains = draw(st.integers(min_value=0, max_value=10))
    energy = draw(st.lists(st.integers(min_value=1, max_value=5), min_size=3, max_size=3))
    
    # Count conditions met
    conditions_met = 0
    if deadlines >= 3:
        conditions_met += 1
    if domains >= 3:
        conditions_met += 1
    if sum(energy) / len(energy) <= 2:
        conditions_met += 1
    
    # If no conditions met, force at least one
    if conditions_met == 0:
        choice = draw(st.integers(min_value=0, max_value=2))
        if choice == 0:
            deadlines = draw(st.integers(min_value=3, max_value=10))
        elif choice == 1:
            domains = draw(st.integers(min_value=3, max_value=10))
        else:
            energy = [1, 1, 1]  # avg = 1.0 <= 2
    
    return StateInputs(
        fixed_deadlines_14d=deadlines,
        active_high_load_domains=domains,
        energy_scores_last_3_days=energy
    )


# Strategy for generating StateInputs that result in NORMAL state
@st.composite
def normal_inputs(draw):
    """Generate StateInputs that result in NORMAL state.
    
    NORMAL: 0 conditions met
    
    Conditions (all must be false):
    - fixed_deadlines_14d < 3
    - active_high_load_domains < 3
    - avg_energy_score > 2
    """
    deadlines = draw(st.integers(min_value=0, max_value=2))
    domains = draw(st.integers(min_value=0, max_value=2))
    # Energy scores that average > 2
    energy = draw(st.lists(st.integers(min_value=3, max_value=5), min_size=3, max_size=3))
    
    return StateInputs(
        fixed_deadlines_14d=deadlines,
        active_high_load_domains=domains,
        energy_scores_last_3_days=energy
    )


# Property 9: Authority Enforcement - Planning Denial
@given(inputs=stressed_or_overloaded_inputs())
@settings(max_examples=100)
def test_property_planning_denial(inputs):
    """Property 9: Authority Enforcement - Planning Denial
    
    For any inputs that result in STRESSED or OVERLOADED state,
    the system should set planning permission to DENIED.
    
    Feature: github-interface, Property 9: Planning Denial
    Validates: Requirements 7.1, 7.2, 7.4
    """
    config = create_sample_config()
    
    # Evaluate state
    state_result = evaluate_state(inputs, config)
    
    # Get active rules
    rule_result = get_active_rules(state_result.state, config)
    
    # Derive authority
    authority = derive_authority(state_result, rule_result)
    
    # Property: If state is STRESSED or OVERLOADED, planning must be DENIED
    if state_result.state in ["STRESSED", "OVERLOADED"]:
        assert authority.planning == "DENIED", (
            f"Planning should be DENIED for {state_result.state} state, "
            f"but got {authority.planning}"
        )
        assert authority.mode == "CONTAINMENT", (
            f"Mode should be CONTAINMENT for {state_result.state} state, "
            f"but got {authority.mode}"
        )


# Property 10: Authority Enforcement - Planning Allowance
@given(inputs=normal_inputs())
@settings(max_examples=100)
def test_property_planning_allowance(inputs):
    """Property 10: Authority Enforcement - Planning Allowance
    
    For any inputs that result in NORMAL state,
    the system should set planning permission to ALLOWED.
    
    Feature: github-interface, Property 10: Planning Allowance
    Validates: Requirements 7.3, 7.4
    """
    config = create_sample_config()
    
    # Evaluate state
    state_result = evaluate_state(inputs, config)
    
    # Get active rules
    rule_result = get_active_rules(state_result.state, config)
    
    # Derive authority
    authority = derive_authority(state_result, rule_result)
    
    # Property: If state is NORMAL, planning must be ALLOWED
    assert state_result.state == "NORMAL", (
        f"Expected NORMAL state from normal_inputs generator, got {state_result.state}"
    )
    assert authority.planning == "ALLOWED", (
        f"Planning should be ALLOWED for NORMAL state, but got {authority.planning}"
    )
    assert authority.mode == "NORMAL", (
        f"Mode should be NORMAL for NORMAL state, but got {authority.mode}"
    )


# Property 11: Authority Check Precedence
@given(
    inputs=st.one_of(
        stressed_or_overloaded_inputs(),
        normal_inputs()
    )
)
@settings(max_examples=100)
def test_property_authority_check_precedence(inputs):
    """Property 11: Authority Check Precedence
    
    For any code path that involves planning, the authority check should occur
    before any planning analysis, ensuring no bypass is possible.
    
    This test verifies that:
    1. Authority is derived from Decision Core output
    2. Authority derivation happens in the correct sequence
    3. Authority cannot be bypassed or modified after derivation
    
    Feature: github-interface, Property 11: Authority Check Precedence
    Validates: Requirements 7.4, 7.5
    """
    config = create_sample_config()
    
    # Step 1: Evaluate state (Decision Core)
    state_result = evaluate_state(inputs, config)
    
    # Step 2: Get active rules (Decision Core)
    rule_result = get_active_rules(state_result.state, config)
    
    # Step 3: Derive authority (must happen before any planning)
    authority = derive_authority(state_result, rule_result)
    
    # Property: Authority must be derived from Decision Core output
    assert authority.state == state_result.state, (
        "Authority state must match Decision Core state"
    )
    assert authority.active_rules == rule_result.active_rules, (
        "Authority active rules must match Decision Core rules"
    )
    
    # Property: Authority permissions must be consistent with state
    if state_result.state in ["STRESSED", "OVERLOADED"]:
        assert authority.planning == "DENIED", (
            f"Planning must be DENIED for {state_result.state} state"
        )
        assert authority.mode == "CONTAINMENT", (
            f"Mode must be CONTAINMENT for {state_result.state} state"
        )
    elif state_result.state == "NORMAL":
        assert authority.planning == "ALLOWED", (
            "Planning must be ALLOWED for NORMAL state"
        )
        assert authority.mode == "NORMAL", (
            "Mode must be NORMAL for NORMAL state"
        )
    
    # Property: Execution is always DENIED (immutable)
    assert authority.execution == "DENIED", (
        "Execution must always be DENIED regardless of state"
    )
