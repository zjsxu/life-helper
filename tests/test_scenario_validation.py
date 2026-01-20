"""Unit tests for required scenario validation.

Tests that all required scenarios exist in the test_scenarios.yaml file
and that each scenario has the expected structure and outputs.

Requirements: 10.1, 10.2, 10.3, 10.4, 21.3, 21.4, 21.5
"""

import pytest
from pathlib import Path

from pl_dss.scenario_runner import load_scenarios


# Test 1: All required basic scenarios exist
def test_required_basic_scenarios_exist():
    """Test that all required basic scenarios exist in test_scenarios.yaml.
    
    Requirements: 10.1, 10.2, 10.3, 10.4
    
    Required scenarios:
    - Sudden Load Spike (OVERLOADED state)
    - Gradual Stress (STRESSED state)
    - Normal Operation (NORMAL state)
    - Recovery Transition (recovery path)
    """
    # Load scenarios from the test file
    scenarios = load_scenarios("scenarios/test_scenarios.yaml")
    
    # Extract scenario names
    scenario_names = [s.name for s in scenarios]
    
    # Check that all required scenarios exist
    required_scenarios = [
        "Sudden Load Spike",
        "Gradual Stress",
        "Normal Operation",
        "Recovery Transition"
    ]
    
    for required_name in required_scenarios:
        assert required_name in scenario_names, \
            f"Required scenario '{required_name}' not found in test_scenarios.yaml"


# Test 2: Sudden Load Spike scenario has expected outputs
def test_sudden_load_spike_has_expected_outputs():
    """Test that Sudden Load Spike scenario has expected outputs defined.
    
    Requirements: 10.1, 10.5
    
    Expected outputs:
    - state: OVERLOADED
    - planning: DENIED
    - execution: DENIED
    - mode: CONTAINMENT
    """
    scenarios = load_scenarios("scenarios/test_scenarios.yaml")
    
    # Find the Sudden Load Spike scenario
    sudden_load_spike = next((s for s in scenarios if s.name == "Sudden Load Spike"), None)
    assert sudden_load_spike is not None, "Sudden Load Spike scenario not found"
    
    # Verify expected outputs are defined
    assert sudden_load_spike.expected is not None, \
        "Sudden Load Spike scenario missing expected outputs"
    
    # Verify expected values
    assert sudden_load_spike.expected.state == "OVERLOADED", \
        "Sudden Load Spike should expect OVERLOADED state"
    assert sudden_load_spike.expected.planning == "DENIED", \
        "Sudden Load Spike should expect planning DENIED"
    assert sudden_load_spike.expected.execution == "DENIED", \
        "Sudden Load Spike should expect execution DENIED"
    assert sudden_load_spike.expected.mode == "CONTAINMENT", \
        "Sudden Load Spike should expect CONTAINMENT mode"


# Test 3: Gradual Stress scenario has expected outputs
def test_gradual_stress_has_expected_outputs():
    """Test that Gradual Stress scenario has expected outputs defined.
    
    Requirements: 10.2, 10.5
    
    Expected outputs:
    - state: STRESSED
    - planning: DENIED
    - execution: DENIED
    - mode: CONTAINMENT
    """
    scenarios = load_scenarios("scenarios/test_scenarios.yaml")
    
    # Find the Gradual Stress scenario
    gradual_stress = next((s for s in scenarios if s.name == "Gradual Stress"), None)
    assert gradual_stress is not None, "Gradual Stress scenario not found"
    
    # Verify expected outputs are defined
    assert gradual_stress.expected is not None, \
        "Gradual Stress scenario missing expected outputs"
    
    # Verify expected values
    assert gradual_stress.expected.state == "STRESSED", \
        "Gradual Stress should expect STRESSED state"
    assert gradual_stress.expected.planning == "DENIED", \
        "Gradual Stress should expect planning DENIED"
    assert gradual_stress.expected.execution == "DENIED", \
        "Gradual Stress should expect execution DENIED"
    assert gradual_stress.expected.mode == "CONTAINMENT", \
        "Gradual Stress should expect CONTAINMENT mode"


# Test 4: Normal Operation scenario has expected outputs
def test_normal_operation_has_expected_outputs():
    """Test that Normal Operation scenario has expected outputs defined.
    
    Requirements: 10.3, 10.5
    
    Expected outputs:
    - state: NORMAL
    - planning: ALLOWED
    - execution: DENIED
    - mode: NORMAL
    """
    scenarios = load_scenarios("scenarios/test_scenarios.yaml")
    
    # Find the Normal Operation scenario
    normal_operation = next((s for s in scenarios if s.name == "Normal Operation"), None)
    assert normal_operation is not None, "Normal Operation scenario not found"
    
    # Verify expected outputs are defined
    assert normal_operation.expected is not None, \
        "Normal Operation scenario missing expected outputs"
    
    # Verify expected values
    assert normal_operation.expected.state == "NORMAL", \
        "Normal Operation should expect NORMAL state"
    assert normal_operation.expected.planning == "ALLOWED", \
        "Normal Operation should expect planning ALLOWED"
    assert normal_operation.expected.execution == "DENIED", \
        "Normal Operation should expect execution DENIED"
    assert normal_operation.expected.mode == "NORMAL", \
        "Normal Operation should expect NORMAL mode"


# Test 5: Recovery Transition scenario has expected outputs
def test_recovery_transition_has_expected_outputs():
    """Test that Recovery Transition scenario has expected outputs defined.
    
    Requirements: 10.4, 10.5
    
    Expected outputs:
    - state: NORMAL
    - planning: ALLOWED
    - execution: DENIED
    - mode: NORMAL
    """
    scenarios = load_scenarios("scenarios/test_scenarios.yaml")
    
    # Find the Recovery Transition scenario
    recovery_transition = next((s for s in scenarios if s.name == "Recovery Transition"), None)
    assert recovery_transition is not None, "Recovery Transition scenario not found"
    
    # Verify expected outputs are defined
    assert recovery_transition.expected is not None, \
        "Recovery Transition scenario missing expected outputs"
    
    # Verify expected values
    assert recovery_transition.expected.state == "NORMAL", \
        "Recovery Transition should expect NORMAL state"
    assert recovery_transition.expected.planning == "ALLOWED", \
        "Recovery Transition should expect planning ALLOWED"
    assert recovery_transition.expected.execution == "DENIED", \
        "Recovery Transition should expect execution DENIED"
    assert recovery_transition.expected.mode == "NORMAL", \
        "Recovery Transition should expect NORMAL mode"


# Test 6: All required advisory scenarios exist
def test_required_advisory_scenarios_exist():
    """Test that all required advisory scenarios exist in test_scenarios.yaml.
    
    Requirements: 21.3, 21.4, 21.5
    
    Required advisory scenarios:
    - Deadline Clustering (deadline clustering detection)
    - Cognitive Overload (cognitive load assessment)
    - Blocked Advisory (blocked advice when OVERLOADED)
    """
    # Load scenarios from the test file
    scenarios = load_scenarios("scenarios/test_scenarios.yaml")
    
    # Extract scenario names
    scenario_names = [s.name for s in scenarios]
    
    # Check that all required advisory scenarios exist
    required_advisory_scenarios = [
        "Deadline Clustering",
        "Cognitive Overload",
        "Blocked Advisory"
    ]
    
    for required_name in required_advisory_scenarios:
        assert required_name in scenario_names, \
            f"Required advisory scenario '{required_name}' not found in test_scenarios.yaml"


# Test 7: Deadline Clustering scenario has expected structure
def test_deadline_clustering_has_expected_structure():
    """Test that Deadline Clustering scenario has expected structure.
    
    Requirements: 21.3
    
    Expected structure:
    - Has tasks defined
    - Has constraints defined
    - Has expected outputs
    - Expected state is NORMAL
    - Expected planning is ALLOWED
    """
    scenarios = load_scenarios("scenarios/test_scenarios.yaml")
    
    # Find the Deadline Clustering scenario
    deadline_clustering = next((s for s in scenarios if s.name == "Deadline Clustering"), None)
    assert deadline_clustering is not None, "Deadline Clustering scenario not found"
    
    # Verify tasks are defined
    assert deadline_clustering.tasks is not None, \
        "Deadline Clustering scenario missing tasks"
    assert len(deadline_clustering.tasks) >= 3, \
        "Deadline Clustering scenario should have at least 3 tasks"
    
    # Verify constraints are defined
    assert deadline_clustering.constraints is not None, \
        "Deadline Clustering scenario missing constraints"
    
    # Verify expected outputs are defined
    assert deadline_clustering.expected is not None, \
        "Deadline Clustering scenario missing expected outputs"
    assert deadline_clustering.expected.state == "NORMAL", \
        "Deadline Clustering should expect NORMAL state"
    assert deadline_clustering.expected.planning == "ALLOWED", \
        "Deadline Clustering should expect planning ALLOWED"


# Test 8: Cognitive Overload scenario has expected structure
def test_cognitive_overload_has_expected_structure():
    """Test that Cognitive Overload scenario has expected structure.
    
    Requirements: 21.4
    
    Expected structure:
    - Has tasks defined
    - Has constraints defined with max_parallel_focus
    - Has expected outputs
    - Expected state is NORMAL
    - Expected planning is ALLOWED
    """
    scenarios = load_scenarios("scenarios/test_scenarios.yaml")
    
    # Find the Cognitive Overload scenario
    cognitive_overload = next((s for s in scenarios if s.name == "Cognitive Overload"), None)
    assert cognitive_overload is not None, "Cognitive Overload scenario not found"
    
    # Verify tasks are defined
    assert cognitive_overload.tasks is not None, \
        "Cognitive Overload scenario missing tasks"
    assert len(cognitive_overload.tasks) > 0, \
        "Cognitive Overload scenario should have tasks"
    
    # Verify constraints are defined
    assert cognitive_overload.constraints is not None, \
        "Cognitive Overload scenario missing constraints"
    assert cognitive_overload.constraints.max_parallel_focus is not None, \
        "Cognitive Overload scenario should have max_parallel_focus constraint"
    
    # Verify expected outputs are defined
    assert cognitive_overload.expected is not None, \
        "Cognitive Overload scenario missing expected outputs"
    assert cognitive_overload.expected.state == "NORMAL", \
        "Cognitive Overload should expect NORMAL state"
    assert cognitive_overload.expected.planning == "ALLOWED", \
        "Cognitive Overload should expect planning ALLOWED"


# Test 9: Blocked Advisory scenario has expected structure
def test_blocked_advisory_has_expected_structure():
    """Test that Blocked Advisory scenario has expected structure.
    
    Requirements: 21.5
    
    Expected structure:
    - Has tasks defined
    - Has constraints defined
    - Has expected outputs
    - Expected state is OVERLOADED
    - Expected planning is DENIED
    """
    scenarios = load_scenarios("scenarios/test_scenarios.yaml")
    
    # Find the Blocked Advisory scenario
    blocked_advisory = next((s for s in scenarios if s.name == "Blocked Advisory"), None)
    assert blocked_advisory is not None, "Blocked Advisory scenario not found"
    
    # Verify tasks are defined
    assert blocked_advisory.tasks is not None, \
        "Blocked Advisory scenario missing tasks"
    
    # Verify constraints are defined
    assert blocked_advisory.constraints is not None, \
        "Blocked Advisory scenario missing constraints"
    
    # Verify expected outputs are defined
    assert blocked_advisory.expected is not None, \
        "Blocked Advisory scenario missing expected outputs"
    assert blocked_advisory.expected.state == "OVERLOADED", \
        "Blocked Advisory should expect OVERLOADED state"
    assert blocked_advisory.expected.planning == "DENIED", \
        "Blocked Advisory should expect planning DENIED"


# Test 10: All scenarios have valid inputs
def test_all_scenarios_have_valid_inputs():
    """Test that all scenarios have valid input structures.
    
    Requirements: 10.1, 10.2, 10.3, 10.4, 21.3, 21.4, 21.5
    
    Valid inputs include:
    - fixed_deadlines_14d (integer)
    - active_high_load_domains (integer)
    - energy_scores_last_3_days (list of 3 integers)
    """
    scenarios = load_scenarios("scenarios/test_scenarios.yaml")
    
    for scenario in scenarios:
        # Verify inputs are defined
        assert scenario.inputs is not None, \
            f"Scenario '{scenario.name}' missing inputs"
        
        # Verify required input fields
        assert hasattr(scenario.inputs, 'fixed_deadlines_14d'), \
            f"Scenario '{scenario.name}' missing fixed_deadlines_14d"
        assert hasattr(scenario.inputs, 'active_high_load_domains'), \
            f"Scenario '{scenario.name}' missing active_high_load_domains"
        assert hasattr(scenario.inputs, 'energy_scores_last_3_days'), \
            f"Scenario '{scenario.name}' missing energy_scores_last_3_days"
        
        # Verify input types
        assert isinstance(scenario.inputs.fixed_deadlines_14d, int), \
            f"Scenario '{scenario.name}' fixed_deadlines_14d should be integer"
        assert isinstance(scenario.inputs.active_high_load_domains, int), \
            f"Scenario '{scenario.name}' active_high_load_domains should be integer"
        assert isinstance(scenario.inputs.energy_scores_last_3_days, list), \
            f"Scenario '{scenario.name}' energy_scores_last_3_days should be list"
        assert len(scenario.inputs.energy_scores_last_3_days) == 3, \
            f"Scenario '{scenario.name}' energy_scores_last_3_days should have 3 values"


# Test 11: Advisory scenarios have valid task structures
def test_advisory_scenarios_have_valid_task_structures():
    """Test that advisory scenarios have valid task structures.
    
    Requirements: 21.3, 21.4, 21.5
    
    Valid task structure includes:
    - name (string)
    - deadline (string in ISO format)
    - type (string)
    """
    scenarios = load_scenarios("scenarios/test_scenarios.yaml")
    
    # Filter to advisory scenarios (those with tasks)
    advisory_scenarios = [s for s in scenarios if s.tasks is not None]
    
    assert len(advisory_scenarios) >= 3, \
        "Should have at least 3 advisory scenarios"
    
    for scenario in advisory_scenarios:
        # Verify each task has required fields
        for task in scenario.tasks:
            assert hasattr(task, 'name'), \
                f"Task in scenario '{scenario.name}' missing name"
            assert hasattr(task, 'deadline'), \
                f"Task in scenario '{scenario.name}' missing deadline"
            assert hasattr(task, 'type'), \
                f"Task in scenario '{scenario.name}' missing type"
            
            # Verify field types
            assert isinstance(task.name, str), \
                f"Task name in scenario '{scenario.name}' should be string"
            assert isinstance(task.deadline, str), \
                f"Task deadline in scenario '{scenario.name}' should be string"
            assert isinstance(task.type, str), \
                f"Task type in scenario '{scenario.name}' should be string"
            
            # Verify deadline format (basic check for YYYY-MM-DD)
            assert len(task.deadline) == 10, \
                f"Task deadline in scenario '{scenario.name}' should be YYYY-MM-DD format"
            assert task.deadline[4] == '-' and task.deadline[7] == '-', \
                f"Task deadline in scenario '{scenario.name}' should be YYYY-MM-DD format"
