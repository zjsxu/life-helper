"""Integration tests for Personal Life Orchestrator.

Tests the complete system flow from Decision Core through Authority
to Planning Engine and Execution Layer, ensuring all layers respect
authority boundaries.

Requirements: 4.1, 4.2, 4.3, 4.4, 8.1, 8.2, 8.3, 8.4
"""

import pytest
import subprocess
import sys
from pathlib import Path

from pl_dss.config import Config, ThresholdConfig, OverloadThresholds, RecoveryThresholds, AuthorityRules
from pl_dss.evaluator import StateInputs, evaluate_state
from pl_dss.rules import get_active_rules
from pl_dss.authority import derive_authority, GlobalAuthority
from pl_dss.planning import PlanRequest, propose_plan, Task, Constraint
from pl_dss.execution import execute_action, ExecutionError
from pl_dss.scenario_runner import (
    Scenario,
    ExpectedOutput,
    load_scenarios,
    run_scenario,
    format_scenario_output,
    validate_scenario_output
)


@pytest.fixture
def sample_config():
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


# Test 1: Complete flow from Decision Core to Authority to Planning
def test_complete_flow_decision_to_planning_overloaded(sample_config):
    """Test complete flow: Decision Core → Authority → Planning (OVERLOADED state).
    
    Validates that when Decision Core determines OVERLOADED state:
    1. Authority is correctly derived with planning DENIED
    2. Planning Engine respects the authority and blocks planning
    
    Requirements: 4.1, 4.3, 8.1
    """
    # Step 1: Create inputs that trigger OVERLOADED state
    inputs = StateInputs(
        fixed_deadlines_14d=4,
        active_high_load_domains=3,
        energy_scores_last_3_days=[2, 2, 2]
    )
    
    # Step 2: Evaluate state using Decision Core
    state_result = evaluate_state(inputs, sample_config)
    assert state_result.state == "OVERLOADED"
    
    # Step 3: Get active rules
    rule_result = get_active_rules(state_result.state, sample_config)
    assert len(rule_result.active_rules) > 0
    
    # Step 4: Derive Global Authority
    authority = derive_authority(state_result, rule_result)
    assert authority.planning == "DENIED"
    assert authority.execution == "DENIED"
    assert authority.mode == "CONTAINMENT"
    
    # Step 5: Attempt planning with DENIED authority
    plan_request = PlanRequest(
        tasks=[],
        constraints=Constraint(),
        decision_state=authority
    )
    plan_result = propose_plan(plan_request)
    
    # Step 6: Verify planning was blocked
    assert plan_result.advisory is None
    assert "ADVICE BLOCKED" in plan_result.reason
    assert "Planning forbidden by Decision Core" in plan_result.reason
    assert plan_result.blocked_by == "Decision Core"


def test_complete_flow_decision_to_planning_normal(sample_config):
    """Test complete flow: Decision Core → Authority → Planning (NORMAL state).
    
    Validates that when Decision Core determines NORMAL state:
    1. Authority is correctly derived with planning ALLOWED
    2. Planning Engine accepts the request but returns not implemented
    
    Requirements: 4.1, 4.3, 8.1
    """
    # Step 1: Create inputs that trigger NORMAL state
    inputs = StateInputs(
        fixed_deadlines_14d=1,
        active_high_load_domains=1,
        energy_scores_last_3_days=[4, 4, 5]
    )
    
    # Step 2: Evaluate state using Decision Core
    state_result = evaluate_state(inputs, sample_config)
    assert state_result.state == "NORMAL"
    
    # Step 3: Get active rules
    rule_result = get_active_rules(state_result.state, sample_config)
    assert len(rule_result.active_rules) == 0
    
    # Step 4: Derive Global Authority
    authority = derive_authority(state_result, rule_result)
    assert authority.planning == "ALLOWED"
    assert authority.execution == "DENIED"
    assert authority.mode == "NORMAL"
    
    # Step 5: Attempt planning with ALLOWED authority
    plan_request = PlanRequest(
        tasks=[],
        constraints=Constraint(),
        decision_state=authority
    )
    plan_result = propose_plan(plan_request)
    
    # Step 6: Verify planning was not blocked but advisory is provided
    assert plan_result.advisory is not None
    assert plan_result.reason == "Advisory analysis complete"
    assert plan_result.blocked_by is None


# Test 2: Complete flow from Decision Core to Authority to Execution
def test_complete_flow_decision_to_execution_always_denied(sample_config):
    """Test complete flow: Decision Core → Authority → Execution (always denied).
    
    Validates that regardless of Decision Core state, execution is always denied
    and raises ExecutionError.
    
    Requirements: 4.2, 4.4, 8.2
    """
    # Test with NORMAL state (planning allowed)
    inputs_normal = StateInputs(
        fixed_deadlines_14d=1,
        active_high_load_domains=1,
        energy_scores_last_3_days=[4, 4, 5]
    )
    state_result = evaluate_state(inputs_normal, sample_config)
    rule_result = get_active_rules(state_result.state, sample_config)
    authority_normal = derive_authority(state_result, rule_result)
    
    assert authority_normal.execution == "DENIED"
    
    with pytest.raises(ExecutionError) as exc_info:
        execute_action(action="any_action", authority=authority_normal)
    assert str(exc_info.value) == "Automation disabled in current system version"
    
    # Test with OVERLOADED state (planning denied)
    inputs_overloaded = StateInputs(
        fixed_deadlines_14d=4,
        active_high_load_domains=3,
        energy_scores_last_3_days=[2, 2, 2]
    )
    state_result = evaluate_state(inputs_overloaded, sample_config)
    rule_result = get_active_rules(state_result.state, sample_config)
    authority_overloaded = derive_authority(state_result, rule_result)
    
    assert authority_overloaded.execution == "DENIED"
    
    with pytest.raises(ExecutionError) as exc_info:
        execute_action(action="any_action", authority=authority_overloaded)
    assert str(exc_info.value) == "Automation disabled in current system version"


# Test 3: Scenario runner end-to-end
def test_scenario_runner_end_to_end(sample_config, tmp_path):
    """Test scenario runner end-to-end with real scenario file.
    
    Validates that:
    1. Scenarios can be loaded from file
    2. Scenarios can be executed through complete system
    3. Output is formatted correctly
    4. Validation works correctly
    
    Requirements: 8.3
    """
    # Create a temporary scenario file
    scenario_file = tmp_path / "test_scenarios.yaml"
    scenario_content = """
scenarios:
  - name: "Test Overload"
    inputs:
      fixed_deadlines_14d: 4
      active_high_load_domains: 3
      energy_scores_last_3_days: [2, 2, 2]
    expected:
      state: OVERLOADED
      planning: DENIED
      execution: DENIED
      mode: CONTAINMENT
  
  - name: "Test Normal"
    inputs:
      fixed_deadlines_14d: 1
      active_high_load_domains: 1
      energy_scores_last_3_days: [4, 4, 5]
    expected:
      state: NORMAL
      planning: ALLOWED
      execution: DENIED
      mode: NORMAL
"""
    scenario_file.write_text(scenario_content)
    
    # Load scenarios
    scenarios = load_scenarios(str(scenario_file))
    assert len(scenarios) == 2
    
    # Run first scenario (OVERLOADED)
    result1 = run_scenario(scenarios[0], sample_config)
    assert result1.authority.state == "OVERLOADED"
    assert result1.authority.planning == "DENIED"
    assert result1.authority.execution == "DENIED"
    assert result1.authority.mode == "CONTAINMENT"
    
    # Validate first scenario
    validation1 = validate_scenario_output(scenarios[0], result1)
    assert validation1.passed
    assert len(validation1.mismatches) == 0
    
    # Format output for first scenario
    output1 = format_scenario_output(result1)
    assert "SCENARIO: Test Overload" in output1
    assert "STATE: OVERLOADED" in output1
    assert "planning: DENIED" in output1
    assert "execution: DENIED" in output1
    assert "MODE: CONTAINMENT" in output1
    
    # Run second scenario (NORMAL)
    result2 = run_scenario(scenarios[1], sample_config)
    assert result2.authority.state == "NORMAL"
    assert result2.authority.planning == "ALLOWED"
    assert result2.authority.execution == "DENIED"
    assert result2.authority.mode == "NORMAL"
    
    # Validate second scenario
    validation2 = validate_scenario_output(scenarios[1], result2)
    assert validation2.passed
    assert len(validation2.mismatches) == 0
    
    # Format output for second scenario
    output2 = format_scenario_output(result2)
    assert "SCENARIO: Test Normal" in output2
    assert "STATE: NORMAL" in output2
    assert "planning: ALLOWED" in output2
    assert "execution: DENIED" in output2
    assert "MODE: NORMAL" in output2


# Test 4: All layers respect authority boundaries
def test_all_layers_respect_authority_boundaries(sample_config):
    """Test that all layers respect authority boundaries.
    
    Validates that:
    1. Planning Engine checks authority before operation
    2. Execution Layer checks authority before operation
    3. No layer can bypass authority enforcement
    
    Requirements: 4.1, 4.2, 4.3, 4.4, 8.4
    """
    # Create OVERLOADED state with DENIED permissions
    inputs_denied = StateInputs(
        fixed_deadlines_14d=4,
        active_high_load_domains=3,
        energy_scores_last_3_days=[2, 2, 2]
    )
    state_result = evaluate_state(inputs_denied, sample_config)
    rule_result = get_active_rules(state_result.state, sample_config)
    authority_denied = derive_authority(state_result, rule_result)
    
    # Verify Planning Engine respects DENIED authority
    plan_request_denied = PlanRequest(
        tasks=[],
        constraints=Constraint(),
        decision_state=authority_denied
    )
    plan_result_denied = propose_plan(plan_request_denied)
    assert plan_result_denied.advisory is None
    assert "ADVICE BLOCKED" in plan_result_denied.reason
    assert "Planning forbidden by Decision Core" in plan_result_denied.reason
    
    # Verify Execution Layer respects DENIED authority (always denied)
    with pytest.raises(ExecutionError):
        execute_action(action="test_action", authority=authority_denied)
    
    # Create NORMAL state with ALLOWED planning
    inputs_allowed = StateInputs(
        fixed_deadlines_14d=1,
        active_high_load_domains=1,
        energy_scores_last_3_days=[4, 4, 5]
    )
    state_result = evaluate_state(inputs_allowed, sample_config)
    rule_result = get_active_rules(state_result.state, sample_config)
    authority_allowed = derive_authority(state_result, rule_result)
    
    # Verify Planning Engine respects ALLOWED authority
    plan_request_allowed = PlanRequest(
        tasks=[],
        constraints=Constraint(),
        decision_state=authority_allowed
    )
    plan_result_allowed = propose_plan(plan_request_allowed)
    # Planning is allowed and advisory is provided
    assert plan_result_allowed.advisory is not None
    assert plan_result_allowed.reason == "Advisory analysis complete"
    
    # Verify Execution Layer still denies even with ALLOWED planning
    with pytest.raises(ExecutionError):
        execute_action(action="test_action", authority=authority_allowed)


# Test 5: CLI commands with real scenario files
def test_cli_scenario_run_command(tmp_path):
    """Test CLI 'scenario run' command with real scenario file.
    
    Requirements: 8.3
    """
    # Create a temporary scenario file
    scenario_file = tmp_path / "cli_test.yaml"
    scenario_content = """
scenarios:
  - name: "CLI Test Scenario"
    inputs:
      fixed_deadlines_14d: 4
      active_high_load_domains: 3
      energy_scores_last_3_days: [2, 2, 2]
"""
    scenario_file.write_text(scenario_content)
    
    # Run CLI command
    result = subprocess.run(
        [sys.executable, "-m", "pl_dss.plo_cli", "scenario", "run", 
         "--name", "CLI Test Scenario", "--file", str(scenario_file)],
        capture_output=True,
        text=True
    )
    
    # Verify command succeeded
    assert result.returncode == 0
    
    # Verify output contains expected sections
    assert "SCENARIO: CLI Test Scenario" in result.stdout
    assert "STATE:" in result.stdout
    assert "AUTHORITY:" in result.stdout
    assert "MODE:" in result.stdout
    assert "ACTIVE RULES:" in result.stdout


def test_cli_scenario_run_all_command(tmp_path):
    """Test CLI 'scenario run-all' command with real scenario file.
    
    Requirements: 8.3
    """
    # Create a temporary scenario file with multiple scenarios
    scenario_file = tmp_path / "cli_test_all.yaml"
    scenario_content = """
scenarios:
  - name: "Scenario 1"
    inputs:
      fixed_deadlines_14d: 4
      active_high_load_domains: 3
      energy_scores_last_3_days: [2, 2, 2]
  
  - name: "Scenario 2"
    inputs:
      fixed_deadlines_14d: 1
      active_high_load_domains: 1
      energy_scores_last_3_days: [4, 4, 5]
"""
    scenario_file.write_text(scenario_content)
    
    # Run CLI command
    result = subprocess.run(
        [sys.executable, "-m", "pl_dss.plo_cli", "scenario", "run-all",
         "--file", str(scenario_file)],
        capture_output=True,
        text=True
    )
    
    # Verify command succeeded
    assert result.returncode == 0
    
    # Verify output contains both scenarios
    assert "SCENARIO: Scenario 1" in result.stdout
    assert "SCENARIO: Scenario 2" in result.stdout


def test_cli_evaluate_command():
    """Test CLI 'evaluate' command.
    
    Requirements: 8.3
    """
    # Run CLI command with OVERLOADED inputs
    result = subprocess.run(
        [sys.executable, "-m", "pl_dss.plo_cli", "evaluate",
         "--deadlines", "4", "--domains", "3", "--energy", "2", "2", "2"],
        capture_output=True,
        text=True
    )
    
    # Verify command succeeded
    assert result.returncode == 0
    
    # Verify output contains expected sections
    assert "STATE:" in result.stdout
    assert "AUTHORITY:" in result.stdout
    assert "MODE:" in result.stdout
    assert "ACTIVE RULES:" in result.stdout


def test_cli_scenario_validate_command(tmp_path):
    """Test CLI 'scenario validate' command.
    
    Requirements: 8.3
    """
    # Create a valid scenario file
    scenario_file = tmp_path / "validate_test.yaml"
    scenario_content = """
scenarios:
  - name: "Valid Scenario"
    inputs:
      fixed_deadlines_14d: 2
      active_high_load_domains: 2
      energy_scores_last_3_days: [3, 3, 3]
"""
    scenario_file.write_text(scenario_content)
    
    # Run CLI command
    result = subprocess.run(
        [sys.executable, "-m", "pl_dss.plo_cli", "scenario", "validate",
         "--file", str(scenario_file)],
        capture_output=True,
        text=True
    )
    
    # Verify command succeeded
    assert result.returncode == 0
    assert "Scenario file is valid" in result.stdout
    assert "Valid Scenario" in result.stdout


# Test 7: Advisory scenario output formatting
def test_advisory_scenario_output_formatting(sample_config, tmp_path):
    """Test that advisory scenarios are formatted correctly in output.
    
    Validates that:
    1. Advisory output is included when planning is ALLOWED
    2. Advisory output follows the correct format (Requirements 19.1, 19.2, 19.3, 19.4)
    3. Blocked advisory shows appropriate message when planning is DENIED
    4. Output includes all required sections
    
    Requirements: 19.1, 19.2, 19.3, 19.4
    """
    # Create advisory scenario file
    scenario_file = tmp_path / "advisory_test.yaml"
    scenario_content = """
advisory_scenarios:
  - name: "Test Advisory Allowed"
    inputs:
      fixed_deadlines_14d: 1
      active_high_load_domains: 1
      energy_scores_last_3_days: [4, 4, 5]
      tasks:
        - name: "Task 1"
          deadline: "2026-02-12"
          type: "coursework"
        - name: "Task 2"
          deadline: "2026-02-11"
          type: "admin"
        - name: "Task 3"
          deadline: "2026-02-13"
          type: "work"
      constraints:
        max_parallel_focus: 2
    expected:
      state: NORMAL
      planning: ALLOWED
      advisory_contains:
        - "3 deadlines"
        - "3-day window"
  
  - name: "Test Advisory Blocked"
    inputs:
      fixed_deadlines_14d: 4
      active_high_load_domains: 3
      energy_scores_last_3_days: [2, 2, 2]
      tasks:
        - name: "Task 1"
          deadline: "2026-02-12"
          type: "work"
      constraints:
        max_parallel_focus: 2
    expected:
      state: OVERLOADED
      planning: DENIED
      advisory_blocked: true
"""
    scenario_file.write_text(scenario_content)
    
    # Load scenarios
    scenarios = load_scenarios(str(scenario_file))
    assert len(scenarios) == 2
    
    # Test scenario 1: Advisory allowed
    result1 = run_scenario(scenarios[0], sample_config)
    output1 = format_scenario_output(result1)
    
    # Verify standard sections are present
    assert "SCENARIO: Test Advisory Allowed" in output1
    assert "STATE: NORMAL" in output1
    assert "AUTHORITY:" in output1
    assert "planning: ALLOWED" in output1
    assert "execution: DENIED" in output1
    assert "MODE: NORMAL" in output1
    assert "ACTIVE RULES:" in output1
    
    # Verify advisory output is present and formatted correctly (Requirements 19.1, 19.2, 19.3, 19.4)
    assert "PLANNING ADVISORY:" in output1  # Requirement 19.1
    assert "- 3 deadlines fall within a 3-day window" in output1  # Requirement 19.2 (bullet points)
    assert "- Recommendation:" in output1  # Requirement 19.3 (nested bullets)
    assert "  •" in output1  # Requirement 19.3 (nested bullet marker)
    
    # Verify no formatting codes (Requirement 19.4)
    assert "**" not in output1  # No markdown bold
    assert "__" not in output1  # No markdown underline
    assert "<" not in output1 or ">" not in output1  # No HTML tags
    
    # Test scenario 2: Advisory blocked
    result2 = run_scenario(scenarios[1], sample_config)
    output2 = format_scenario_output(result2)
    
    # Verify standard sections are present
    assert "SCENARIO: Test Advisory Blocked" in output2
    assert "STATE: OVERLOADED" in output2
    assert "planning: DENIED" in output2
    
    # Verify blocked message is present instead of advisory
    assert "ADVICE BLOCKED" in output2
    assert "Planning forbidden by Decision Core" in output2
    
    # Verify no advisory analysis is present
    assert "PLANNING ADVISORY:" not in output2
    assert "Recommendation:" not in output2


# Test 8: Advisory scenario with real test_scenarios.yaml file
def test_advisory_scenarios_from_real_file(sample_config):
    """Test advisory scenarios from the actual test_scenarios.yaml file.
    
    Validates that all advisory scenarios in the real file work correctly
    and produce properly formatted output.
    
    Requirements: 19.1, 19.2, 19.3, 19.4, 21.1, 21.2
    """
    # Load scenarios from real file
    scenarios = load_scenarios("scenarios/test_scenarios.yaml")
    
    # Find advisory scenarios
    advisory_scenarios = [s for s in scenarios if s.tasks is not None]
    assert len(advisory_scenarios) >= 3  # Should have at least 3 advisory scenarios
    
    # Test each advisory scenario
    for scenario in advisory_scenarios:
        result = run_scenario(scenario, sample_config)
        output = format_scenario_output(result)
        
        # Verify output contains required sections
        assert f"SCENARIO: {scenario.name}" in output
        assert "STATE:" in output
        assert "AUTHORITY:" in output
        assert "MODE:" in output
        assert "ACTIVE RULES:" in output
        
        # Check if planning was allowed or denied
        if result.authority.planning == "ALLOWED":
            # Should have advisory output
            assert "PLANNING ADVISORY:" in output
            # Should have bullet points for observations
            assert "\n- " in output
            # If there are recommendations, should have nested bullets
            if result.plan_result and result.plan_result.advisory and result.plan_result.advisory.recommendations:
                assert "  •" in output
        else:
            # Should have blocked message
            assert "ADVICE BLOCKED" in output
            assert "Planning forbidden by Decision Core" in output
            # Should NOT have advisory output
            assert "PLANNING ADVISORY:" not in output


# Test 6: Authority enforcement across state transitions
def test_authority_enforcement_across_state_transitions(sample_config):
    """Test that authority is correctly enforced across state transitions.
    
    Validates that as system state changes, authority permissions change
    accordingly and all layers respect the new authority.
    
    Requirements: 4.1, 4.2, 4.3, 4.4, 8.4
    """
    # Start in NORMAL state
    inputs_normal = StateInputs(
        fixed_deadlines_14d=1,
        active_high_load_domains=1,
        energy_scores_last_3_days=[4, 4, 5]
    )
    state_result = evaluate_state(inputs_normal, sample_config)
    rule_result = get_active_rules(state_result.state, sample_config)
    authority = derive_authority(state_result, rule_result)
    
    assert authority.state == "NORMAL"
    assert authority.planning == "ALLOWED"
    assert authority.execution == "DENIED"
    
    # Planning should not be blocked
    plan_request = PlanRequest(tasks=[], constraints=Constraint(), decision_state=authority)
    plan_result = propose_plan(plan_request)
    assert plan_result.advisory is not None
    assert plan_result.reason == "Advisory analysis complete"
    
    # Transition to STRESSED state
    inputs_stressed = StateInputs(
        fixed_deadlines_14d=3,
        active_high_load_domains=2,
        energy_scores_last_3_days=[3, 3, 3]
    )
    state_result = evaluate_state(inputs_stressed, sample_config)
    rule_result = get_active_rules(state_result.state, sample_config)
    authority = derive_authority(state_result, rule_result)
    
    assert authority.state == "STRESSED"
    assert authority.planning == "DENIED"
    assert authority.execution == "DENIED"
    
    # Planning should now be blocked
    plan_request = PlanRequest(tasks=[], constraints=Constraint(), decision_state=authority)
    plan_result = propose_plan(plan_request)
    assert "ADVICE BLOCKED" in plan_result.reason
    assert "Planning forbidden by Decision Core" in plan_result.reason
    
    # Transition to OVERLOADED state
    inputs_overloaded = StateInputs(
        fixed_deadlines_14d=4,
        active_high_load_domains=3,
        energy_scores_last_3_days=[2, 2, 2]
    )
    state_result = evaluate_state(inputs_overloaded, sample_config)
    rule_result = get_active_rules(state_result.state, sample_config)
    authority = derive_authority(state_result, rule_result)
    
    assert authority.state == "OVERLOADED"
    assert authority.planning == "DENIED"
    assert authority.execution == "DENIED"
    
    # Planning should still be blocked
    plan_request = PlanRequest(tasks=[], constraints=Constraint(), decision_state=authority)
    plan_result = propose_plan(plan_request)
    assert "ADVICE BLOCKED" in plan_result.reason
    assert "Planning forbidden by Decision Core" in plan_result.reason
    
    # Execution should always be denied regardless of state
    with pytest.raises(ExecutionError):
        execute_action(action="test", authority=authority)
