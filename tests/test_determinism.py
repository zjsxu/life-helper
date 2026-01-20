"""Property-based tests for deterministic behavior.

Feature: personal-decision-support-system, Property 8: Deterministic Behavior
Validates: Requirements 6.2
"""

from hypothesis import given, strategies as st, settings

from pl_dss.config import Config, ThresholdConfig, OverloadThresholds, RecoveryThresholds
from pl_dss.evaluator import StateInputs, evaluate_state
from pl_dss.rules import get_active_rules
from pl_dss.recovery import check_recovery
from pl_dss.main import run_system, format_output


def create_sample_config():
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


# Strategy for generating valid energy scores (3 integers between 1 and 5)
energy_scores_strategy = st.lists(
    st.integers(min_value=1, max_value=5),
    min_size=3,
    max_size=3
)

# Strategy for generating non-negative integers
non_negative_int_strategy = st.integers(min_value=0, max_value=100)

# Strategy for generating valid StateInputs
state_inputs_strategy = st.builds(
    StateInputs,
    fixed_deadlines_14d=non_negative_int_strategy,
    active_high_load_domains=non_negative_int_strategy,
    energy_scores_last_3_days=energy_scores_strategy
)


@given(inputs=state_inputs_strategy)
@settings(max_examples=100)
def test_deterministic_state_evaluation(inputs):
    """Property 8: Deterministic Behavior - State evaluation.
    
    For any valid inputs, running evaluate_state multiple times with the same
    inputs and configuration should produce identical results every time.
    
    Feature: personal-decision-support-system, Property 8: Deterministic Behavior
    Validates: Requirements 6.2
    """
    config = create_sample_config()
    
    # Run evaluation multiple times
    result1 = evaluate_state(inputs, config)
    result2 = evaluate_state(inputs, config)
    result3 = evaluate_state(inputs, config)
    
    # All results should be identical
    assert result1.state == result2.state == result3.state
    assert result1.explanation == result2.explanation == result3.explanation
    assert result1.conditions_met == result2.conditions_met == result3.conditions_met


@given(inputs=state_inputs_strategy)
@settings(max_examples=100)
def test_deterministic_rule_engine(inputs):
    """Property 8: Deterministic Behavior - Rule engine.
    
    For any valid inputs, running the rule engine multiple times with the same
    state should produce identical results every time.
    
    Feature: personal-decision-support-system, Property 8: Deterministic Behavior
    Validates: Requirements 6.2
    """
    config = create_sample_config()
    
    # First get the state
    state_result = evaluate_state(inputs, config)
    
    # Run rule engine multiple times
    rule_result1 = get_active_rules(state_result.state, config)
    rule_result2 = get_active_rules(state_result.state, config)
    rule_result3 = get_active_rules(state_result.state, config)
    
    # All results should be identical
    assert rule_result1.state == rule_result2.state == rule_result3.state
    assert rule_result1.active_rules == rule_result2.active_rules == rule_result3.active_rules


@given(inputs=state_inputs_strategy)
@settings(max_examples=100)
def test_deterministic_recovery_monitor(inputs):
    """Property 8: Deterministic Behavior - Recovery monitor.
    
    For any valid inputs, running the recovery monitor multiple times with the
    same inputs should produce identical results every time.
    
    Feature: personal-decision-support-system, Property 8: Deterministic Behavior
    Validates: Requirements 6.2
    """
    config = create_sample_config()
    
    # First get the state
    state_result = evaluate_state(inputs, config)
    
    # Run recovery monitor multiple times
    recovery_result1 = check_recovery(inputs, state_result.state, config)
    recovery_result2 = check_recovery(inputs, state_result.state, config)
    recovery_result3 = check_recovery(inputs, state_result.state, config)
    
    # All results should be identical
    assert recovery_result1.can_recover == recovery_result2.can_recover == recovery_result3.can_recover
    assert recovery_result1.explanation == recovery_result2.explanation == recovery_result3.explanation
    assert recovery_result1.blocking_conditions == recovery_result2.blocking_conditions == recovery_result3.blocking_conditions


@given(inputs=state_inputs_strategy)
@settings(max_examples=100)
def test_deterministic_complete_system(inputs):
    """Property 8: Deterministic Behavior - Complete system.
    
    For any valid inputs, running the complete system multiple times with the
    same inputs and configuration should produce identical output every time.
    
    Feature: personal-decision-support-system, Property 8: Deterministic Behavior
    Validates: Requirements 6.2
    """
    config = create_sample_config()
    
    # Run complete system pipeline multiple times
    state1, rules1, recovery1 = run_system(inputs, config)
    state2, rules2, recovery2 = run_system(inputs, config)
    state3, rules3, recovery3 = run_system(inputs, config)
    
    # All state results should be identical
    assert state1.state == state2.state == state3.state
    assert state1.explanation == state2.explanation == state3.explanation
    assert state1.conditions_met == state2.conditions_met == state3.conditions_met
    
    # All rule results should be identical
    assert rules1.state == rules2.state == rules3.state
    assert rules1.active_rules == rules2.active_rules == rules3.active_rules
    
    # All recovery results should be identical
    assert recovery1.can_recover == recovery2.can_recover == recovery3.can_recover
    assert recovery1.explanation == recovery2.explanation == recovery3.explanation
    assert recovery1.blocking_conditions == recovery2.blocking_conditions == recovery3.blocking_conditions


@given(inputs=state_inputs_strategy)
@settings(max_examples=100)
def test_deterministic_output_formatting(inputs):
    """Property 8: Deterministic Behavior - Output formatting.
    
    For any valid inputs, formatting the output multiple times with the same
    results should produce identical text every time.
    
    Feature: personal-decision-support-system, Property 8: Deterministic Behavior
    Validates: Requirements 6.2
    """
    config = create_sample_config()
    
    # Run system once to get results
    state_result, rule_result, recovery_result = run_system(inputs, config)
    
    # Format output multiple times
    output1 = format_output(state_result, rule_result, recovery_result)
    output2 = format_output(state_result, rule_result, recovery_result)
    output3 = format_output(state_result, rule_result, recovery_result)
    
    # All outputs should be identical
    assert output1 == output2 == output3
