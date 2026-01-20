"""Scenario Runner module for Personal Life Orchestrator.

This module provides scenario-based demonstration of system behavior.
Scenarios can be loaded from YAML or JSON files and executed to show
how the system responds to different inputs.

Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 10.5
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import yaml

from pl_dss.evaluator import StateInputs, StateResult, evaluate_state
from pl_dss.rules import RuleResult, get_active_rules
from pl_dss.authority import GlobalAuthority, derive_authority
from pl_dss.config import Config
from pl_dss.planning import Task, Constraint, PlanRequest, PlanResult, propose_plan, format_advisory_output


@dataclass
class ExpectedOutput:
    """Expected output for scenario validation.
    
    Attributes:
        state: Expected system state ("NORMAL", "STRESSED", or "OVERLOADED")
        planning: Expected planning permission ("ALLOWED" or "DENIED")
        execution: Expected execution permission ("ALLOWED" or "DENIED")
        mode: Expected authority mode ("NORMAL", "CONTAINMENT", or "RECOVERY")
    """
    state: str
    planning: str
    execution: str
    mode: str


@dataclass
class Scenario:
    """Scenario definition for testing system behavior.
    
    Attributes:
        name: Human-readable scenario name
        inputs: StateInputs for Decision Core evaluation
        expected: Expected outputs for validation (optional)
        tasks: List of tasks for Planning Advisor (optional)
        constraints: Constraints for Planning Advisor (optional)
    """
    name: str
    inputs: StateInputs
    expected: Optional[ExpectedOutput] = None
    tasks: Optional[List[Task]] = None
    constraints: Optional[Constraint] = None


@dataclass
class ScenarioResult:
    """Result from running a scenario.
    
    Attributes:
        scenario_name: Name of the scenario that was run
        state_result: StateResult from Decision Core evaluation
        rule_result: RuleResult from rule engine
        authority: GlobalAuthority derived from Decision Core output
        plan_result: PlanResult from Planning Advisor (optional)
    """
    scenario_name: str
    state_result: StateResult
    rule_result: RuleResult
    authority: GlobalAuthority
    plan_result: Optional[PlanResult] = None


class ScenarioError(Exception):
    """Raised when scenario loading or execution fails."""
    pass



def load_scenarios(filepath: str) -> List[Scenario]:
    """Load scenarios from YAML or JSON file.
    
    Supports both YAML and JSON formats. File format is determined by extension.
    
    Args:
        filepath: Path to scenario file (.yaml, .yml, or .json)
        
    Returns:
        List of Scenario objects loaded from file
        
    Raises:
        ScenarioError: If file not found, parse error, or invalid structure
        
    Requirements: 5.1
    """
    path = Path(filepath)
    
    # Check if file exists
    if not path.exists():
        raise ScenarioError(
            f"Scenario file not found: {filepath}\n"
            f"Expected: A valid YAML or JSON file at {filepath}"
        )
    
    # Determine file format and load
    try:
        with open(path, 'r') as f:
            if path.suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            elif path.suffix == '.json':
                data = json.load(f)
            else:
                raise ScenarioError(
                    f"Unsupported file format: {path.suffix}\n"
                    f"Expected: .yaml, .yml, or .json file"
                )
    except yaml.YAMLError as e:
        raise ScenarioError(
            f"Failed to parse YAML file: {filepath}\n"
            f"Details: {str(e)}\n"
            f"Expected: Valid YAML syntax"
        )
    except json.JSONDecodeError as e:
        raise ScenarioError(
            f"Failed to parse JSON file: {filepath}\n"
            f"Details: {str(e)}\n"
            f"Expected: Valid JSON syntax"
        )
    except Exception as e:
        raise ScenarioError(
            f"Failed to read scenario file: {filepath}\n"
            f"Details: {str(e)}"
        )
    
    # Validate structure
    if data is None:
        raise ScenarioError(
            f"Scenario file is empty: {filepath}\n"
            f"Expected: File with 'scenarios' key containing list of scenarios"
        )
    
    if not isinstance(data, dict):
        raise ScenarioError(
            f"Invalid scenario file structure: {filepath}\n"
            f"Details: Root must be a dictionary\n"
            f"Expected: Dictionary with 'scenarios' or 'advisory_scenarios' key"
        )
    
    if 'scenarios' not in data and 'advisory_scenarios' not in data:
        raise ScenarioError(
            f"Missing scenario keys in file: {filepath}\n"
            f"Expected: File must contain 'scenarios' or 'advisory_scenarios' key"
        )
    
    # Parse scenarios
    scenarios = []
    
    # Load regular scenarios
    if 'scenarios' in data and isinstance(data['scenarios'], list):
        for i, scenario_data in enumerate(data['scenarios']):
            try:
                scenario = _parse_scenario(scenario_data, i)
                scenarios.append(scenario)
            except ScenarioError as e:
                raise ScenarioError(
                    f"Invalid scenario at index {i} in file: {filepath}\n"
                    f"Details: {str(e)}"
                )
    
    # Load advisory scenarios
    if 'advisory_scenarios' in data and isinstance(data['advisory_scenarios'], list):
        for i, scenario_data in enumerate(data['advisory_scenarios']):
            try:
                scenario = _parse_scenario(scenario_data, i)
                scenarios.append(scenario)
            except ScenarioError as e:
                raise ScenarioError(
                    f"Invalid advisory scenario at index {i} in file: {filepath}\n"
                    f"Details: {str(e)}"
                )
    
    if len(scenarios) == 0:
        raise ScenarioError(
            f"No scenarios found in file: {filepath}\n"
            f"Expected: At least one scenario in 'scenarios' or 'advisory_scenarios' list"
        )
    
    return scenarios


def _parse_scenario(data: Dict[str, Any], index: int) -> Scenario:
    """Parse a single scenario from dictionary data.
    
    Args:
        data: Dictionary containing scenario data
        index: Index of scenario in list (for error messages)
        
    Returns:
        Scenario object
        
    Raises:
        ScenarioError: If scenario structure is invalid
    """
    if not isinstance(data, dict):
        raise ScenarioError(
            f"Scenario must be a dictionary, got {type(data).__name__}"
        )
    
    # Validate required fields
    if 'name' not in data:
        raise ScenarioError("Missing required field: 'name'")
    
    if 'inputs' not in data:
        raise ScenarioError("Missing required field: 'inputs'")
    
    # Parse inputs
    inputs_data = data['inputs']
    if not isinstance(inputs_data, dict):
        raise ScenarioError(
            f"'inputs' must be a dictionary, got {type(inputs_data).__name__}"
        )
    
    # Validate required input fields
    required_input_fields = ['fixed_deadlines_14d', 'active_high_load_domains', 'energy_scores_last_3_days']
    for field in required_input_fields:
        if field not in inputs_data:
            raise ScenarioError(f"Missing required input field: '{field}'")
    
    # Create StateInputs
    try:
        inputs = StateInputs(
            fixed_deadlines_14d=inputs_data['fixed_deadlines_14d'],
            active_high_load_domains=inputs_data['active_high_load_domains'],
            energy_scores_last_3_days=inputs_data['energy_scores_last_3_days']
        )
    except Exception as e:
        raise ScenarioError(f"Failed to create StateInputs: {str(e)}")
    
    # Parse tasks (optional)
    tasks = None
    if 'tasks' in inputs_data:
        tasks_data = inputs_data['tasks']
        if not isinstance(tasks_data, list):
            raise ScenarioError(
                f"'tasks' must be a list, got {type(tasks_data).__name__}"
            )
        
        tasks = []
        for i, task_data in enumerate(tasks_data):
            if not isinstance(task_data, dict):
                raise ScenarioError(
                    f"Task at index {i} must be a dictionary, got {type(task_data).__name__}"
                )
            
            # Validate required task fields
            required_task_fields = ['name', 'deadline', 'type']
            for field in required_task_fields:
                if field not in task_data:
                    raise ScenarioError(f"Task at index {i} missing required field: '{field}'")
            
            try:
                task = Task(
                    name=task_data['name'],
                    deadline=task_data['deadline'],
                    type=task_data['type']
                )
                tasks.append(task)
            except Exception as e:
                raise ScenarioError(f"Failed to create Task at index {i}: {str(e)}")
    
    # Parse constraints (optional)
    constraints = None
    if 'constraints' in inputs_data:
        constraints_data = inputs_data['constraints']
        if not isinstance(constraints_data, dict):
            raise ScenarioError(
                f"'constraints' must be a dictionary, got {type(constraints_data).__name__}"
            )
        
        try:
            constraints = Constraint(
                max_parallel_focus=constraints_data.get('max_parallel_focus'),
                no_work_after=constraints_data.get('no_work_after')
            )
        except Exception as e:
            raise ScenarioError(f"Failed to create Constraint: {str(e)}")
    
    # Parse expected output (optional)
    expected = None
    if 'expected' in data:
        expected_data = data['expected']
        if not isinstance(expected_data, dict):
            raise ScenarioError(
                f"'expected' must be a dictionary, got {type(expected_data).__name__}"
            )
        
        # For advisory scenarios, expected fields may be different
        # Check if this is a regular scenario or advisory scenario
        is_advisory_scenario = 'advisory_contains' in expected_data or 'advisory_blocked' in expected_data
        
        if not is_advisory_scenario:
            # Regular scenario - validate required expected fields
            required_expected_fields = ['state', 'planning', 'execution', 'mode']
            for field in required_expected_fields:
                if field not in expected_data:
                    raise ScenarioError(f"Missing required expected field: '{field}'")
            
            try:
                expected = ExpectedOutput(
                    state=expected_data['state'],
                    planning=expected_data['planning'],
                    execution=expected_data['execution'],
                    mode=expected_data['mode']
                )
            except Exception as e:
                raise ScenarioError(f"Failed to create ExpectedOutput: {str(e)}")
        else:
            # Advisory scenario - only require state and planning
            if 'state' not in expected_data:
                raise ScenarioError("Missing required expected field: 'state'")
            if 'planning' not in expected_data:
                raise ScenarioError("Missing required expected field: 'planning'")
            
            # Use default values for execution and mode based on state
            state = expected_data['state']
            default_mode = 'CONTAINMENT' if state in ['OVERLOADED', 'STRESSED'] else 'NORMAL'
            
            try:
                expected = ExpectedOutput(
                    state=state,
                    planning=expected_data['planning'],
                    execution=expected_data.get('execution', 'DENIED'),  # Default to DENIED
                    mode=expected_data.get('mode', default_mode)  # Default based on state
                )
            except Exception as e:
                raise ScenarioError(f"Failed to create ExpectedOutput: {str(e)}")
    
    return Scenario(
        name=data['name'],
        inputs=inputs,
        expected=expected,
        tasks=tasks,
        constraints=constraints
    )



def run_scenario(scenario: Scenario, config: Config) -> ScenarioResult:
    """Run a single scenario through the system.
    
    Steps:
    1. Evaluate state using Decision Core (evaluate_state)
    2. Get active rules from rule engine
    3. Derive Global Authority from Decision Core output
    4. Call Planning Advisor if tasks are present
    5. Collect all outputs
    
    Args:
        scenario: Scenario to run
        config: System configuration
        
    Returns:
        ScenarioResult with all outputs (state, authority, rules, advisory)
        
    Raises:
        ScenarioError: If scenario execution fails
        
    Requirements: 5.2, 5.3, 21.1, 21.2
    """
    try:
        # Step 1: Evaluate state using Decision Core
        state_result = evaluate_state(scenario.inputs, config)
        
        # Step 2: Get active rules from rule engine
        rule_result = get_active_rules(state_result.state, config)
        
        # Step 3: Derive Global Authority from Decision Core output
        authority = derive_authority(state_result, rule_result)
        
        # Step 4: Call Planning Advisor if tasks are present (Requirements 21.1, 21.2)
        plan_result = None
        if scenario.tasks is not None:
            # Create PlanRequest with tasks and constraints
            constraints = scenario.constraints if scenario.constraints is not None else Constraint()
            plan_request = PlanRequest(
                tasks=scenario.tasks,
                constraints=constraints,
                decision_state=authority
            )
            plan_result = propose_plan(plan_request)
        
        # Step 5: Collect all outputs
        return ScenarioResult(
            scenario_name=scenario.name,
            state_result=state_result,
            rule_result=rule_result,
            authority=authority,
            plan_result=plan_result
        )
        
    except Exception as e:
        raise ScenarioError(
            f"Failed to run scenario '{scenario.name}'\n"
            f"Details: {str(e)}"
        )



def format_scenario_output(result: ScenarioResult) -> str:
    """Format scenario output in strict format.
    
    Output format:
    SCENARIO: {name}
    STATE: {state}
    AUTHORITY:
    - planning: {ALLOWED|DENIED}
    - execution: {ALLOWED|DENIED}
    MODE: {mode}
    ACTIVE RULES:
    - {rule1}
    - {rule2}
    
    Or if no rules:
    ACTIVE RULES:
    (none)
    
    If advisory output is present:
    
    {formatted advisory output}
    
    Args:
        result: ScenarioResult from running a scenario
        
    Returns:
        Formatted output string following strict format
        
    Requirements: 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 19.1, 19.2, 19.3, 19.4
    """
    lines = []
    
    # SCENARIO line
    lines.append(f"SCENARIO: {result.scenario_name}")
    
    # STATE line
    lines.append(f"STATE: {result.authority.state}")
    
    # AUTHORITY section
    lines.append("AUTHORITY:")
    lines.append(f"- planning: {result.authority.planning}")
    lines.append(f"- execution: {result.authority.execution}")
    
    # MODE line
    lines.append(f"MODE: {result.authority.mode}")
    
    # ACTIVE RULES section
    lines.append("ACTIVE RULES:")
    if result.authority.active_rules:
        for rule in result.authority.active_rules:
            lines.append(f"- {rule}")
    else:
        lines.append("(none)")
    
    # Add advisory output if present (Requirements 19.1, 19.2, 19.3, 19.4)
    if result.plan_result is not None:
        lines.append("")  # Blank line before advisory
        if result.plan_result.advisory is not None:
            # Format advisory output
            advisory_text = format_advisory_output(result.plan_result.advisory)
            lines.append(advisory_text)
        else:
            # Planning was blocked - show the reason
            lines.append(result.plan_result.reason)
    
    return "\n".join(lines)



@dataclass
class ValidationResult:
    """Result from validating scenario output.
    
    Attributes:
        passed: Whether validation passed
        mismatches: List of mismatch descriptions (empty if passed)
    """
    passed: bool
    mismatches: List[str]


def validate_scenario_output(scenario: Scenario, result: ScenarioResult) -> ValidationResult:
    """Validate scenario output against expected output.
    
    Compares actual output with expected output and reports mismatches.
    
    Args:
        scenario: Scenario with expected output
        result: ScenarioResult with actual output
        
    Returns:
        ValidationResult with pass/fail status and list of mismatches
        
    Requirements: 10.5
    """
    # If no expected output defined, validation passes
    if scenario.expected is None:
        return ValidationResult(passed=True, mismatches=[])
    
    mismatches = []
    expected = scenario.expected
    
    # Check state
    if result.authority.state != expected.state:
        mismatches.append(
            f"State mismatch: expected '{expected.state}', got '{result.authority.state}'"
        )
    
    # Check planning permission
    if result.authority.planning != expected.planning:
        mismatches.append(
            f"Planning permission mismatch: expected '{expected.planning}', got '{result.authority.planning}'"
        )
    
    # Check execution permission
    if result.authority.execution != expected.execution:
        mismatches.append(
            f"Execution permission mismatch: expected '{expected.execution}', got '{result.authority.execution}'"
        )
    
    # Check mode
    if result.authority.mode != expected.mode:
        mismatches.append(
            f"Mode mismatch: expected '{expected.mode}', got '{result.authority.mode}'"
        )
    
    passed = len(mismatches) == 0
    
    return ValidationResult(passed=passed, mismatches=mismatches)
