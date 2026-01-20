# Design Document: Personal Life Orchestrator (PLO)

## Overview

The Personal Life Orchestrator (PLO) is a safety-first personal autonomous system that extends the existing Decision Core (PL-DSS) with layered authority and strict control boundaries. The system implements three layers:

- **L0 (Decision Core)**: Existing PL-DSS that evaluates system state
- **L1 (Planning Engine)**: Interface-only layer for future planning functionality
- **L2 (Execution Layer)**: Explicitly disabled automation layer

All authority flows from L0 to downstream layers through a Global Authority object. The system is designed to be demonstrable via scenario-based runs without requiring a GUI.

## Architecture

### Layered Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CLI / Scenario Runner                 │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   Global Authority                       │
│  (Derived from Decision Core output)                     │
│  - planning: ALLOWED | DENIED                            │
│  - execution: ALLOWED | DENIED                           │
│  - mode: NORMAL | CONTAINMENT | RECOVERY                 │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  L0: Decision│   │ L1: Planning │   │ L2: Execution│
│     Core     │   │    Engine    │   │    Layer     │
│  (Existing)  │   │  (Interface) │   │  (Disabled)  │
└──────────────┘   └──────────────┘   └──────────────┘
```

### Module Responsibilities

**L0: Decision Core (Existing PL-DSS)**
- Evaluates system state (NORMAL, STRESSED, OVERLOADED)
- Provides downgrade rules based on state
- Monitors recovery conditions
- Operates independently without knowledge of L1 or L2

**Global Authority Module (New)**
- Derives authority from Decision Core output
- Provides authority object to all downstream modules
- Maps system states to permissions
- Enforces authority contracts

**L1: Planning Engine (New - Advisory Implementation)**
- Provides `propose_plan()` interface
- Implements Planning Advisor for high-level task analysis
- Checks Global Authority before any operation
- Returns blocked message when planning is denied
- Provides descriptive, non-prescriptive advice when allowed
- Does NOT implement scheduling, calendar modification, or optimization

**L2: Execution Layer (New - Explicitly Disabled)**
- Placeholder module only
- Raises `ExecutionError` on any execution attempt
- Documents that automation is forbidden
- Does NOT implement any automation functionality

**Scenario Runner (New)**
- Loads scenarios from YAML/JSON
- Runs scenarios through the system
- Outputs results in strict format
- Demonstrates system behavior without GUI

## Components and Interfaces

### Global Authority Module

**Data Structure:**
```python
@dataclass
class GlobalAuthority:
    planning: str  # "ALLOWED" | "DENIED"
    execution: str  # "ALLOWED" | "DENIED"
    mode: str  # "NORMAL" | "CONTAINMENT" | "RECOVERY"
    state: str  # "NORMAL" | "STRESSED" | "OVERLOADED"
    active_rules: List[str]
```

**Core Function:**
```python
def derive_authority(state_result: StateResult, rule_result: RuleResult) -> GlobalAuthority:
    """
    Derives Global Authority from Decision Core output.
    
    Authority Derivation Rules:
    - OVERLOADED → planning: DENIED, mode: CONTAINMENT
    - STRESSED → planning: DENIED, mode: CONTAINMENT
    - NORMAL → planning: ALLOWED, mode: NORMAL
    - execution: ALWAYS DENIED in this version
    
    Args:
        state_result: Output from Decision Core state evaluation
        rule_result: Output from Decision Core rule engine
        
    Returns:
        GlobalAuthority object with all permissions and mode
    """
```

### Planning Engine (L1)

**Input Data Structure:**
```python
@dataclass
class Task:
    name: str
    deadline: str  # ISO format date: "YYYY-MM-DD"
    type: str  # "coursework", "admin", "work", etc.

@dataclass
class Constraint:
    max_parallel_focus: Optional[int]  # Maximum tasks to focus on simultaneously
    no_work_after: Optional[str]  # Time boundary: "HH:MM" format

@dataclass
class PlanRequest:
    tasks: List[Task]
    constraints: Constraint
    decision_state: GlobalAuthority
```

**Output Data Structure:**
```python
@dataclass
class AdvisoryOutput:
    observations: List[str]  # Descriptive observations about workload
    recommendations: List[str]  # High-level suggestions (not prescriptive)
    warnings: List[str]  # Risk flags and conflict warnings

@dataclass
class PlanResult:
    advisory: Optional[AdvisoryOutput]  # None when planning denied
    reason: str  # Explanation of result
    blocked_by: Optional[str]  # "Decision Core" when denied
```

**Core Function:**
```python
def propose_plan(request: PlanRequest) -> PlanResult:
    """
    Planning Advisor that provides high-level task analysis.
    
    When planning is ALLOWED:
    - Analyzes deadline clustering
    - Assesses cognitive load
    - Provides prioritization suggestions
    - Warns about conflicts
    - Returns descriptive, non-prescriptive advice
    
    When planning is DENIED:
    - Returns blocked message
    - Provides no analysis or suggestions
    
    NEVER:
    - Schedules specific times
    - Modifies calendars
    - Executes actions
    - Uses optimization language
    
    Args:
        request: PlanRequest with tasks, constraints, and authority
        
    Returns:
        PlanResult with advisory output or blocked message
    """
```

**Advisory Analysis Functions:**
```python
def analyze_deadline_clustering(tasks: List[Task]) -> List[str]:
    """
    Detect when multiple deadlines fall within tight windows.
    
    Returns observations like:
    - "3 deadlines fall within a 3-day window"
    - "Deadlines cluster between Feb 11-13"
    """

def assess_cognitive_load(tasks: List[Task], constraints: Constraint) -> List[str]:
    """
    Assess if workload exceeds safe thresholds.
    
    Returns observations like:
    - "Cognitive load likely exceeds safe threshold"
    - "This week exceeds your usual load"
    """

def suggest_prioritization(tasks: List[Task]) -> List[str]:
    """
    Provide high-level prioritization suggestions.
    
    Returns recommendations like:
    - "Treat coursework as primary focus"
    - "Minimize administrative scope"
    - "Avoid adding optional tasks this week"
    """

def detect_conflicts(tasks: List[Task], constraints: Constraint) -> List[str]:
    """
    Warn about potential conflicts and constraint violations.
    
    Returns warnings like:
    - "Multiple high-priority tasks overlap"
    - "Task load exceeds max_parallel_focus constraint"
    """
```

### Execution Layer (L2)

**Error Class:**
```python
class ExecutionError(Exception):
    """Raised when execution is attempted in disabled system."""
    pass
```

**Placeholder Function:**
```python
def execute_action(action: Any, authority: GlobalAuthority) -> None:
    """
    Execution is explicitly disabled in this system version.
    
    This function exists to:
    1. Document that execution layer exists conceptually
    2. Fail loudly if execution is attempted
    3. Provide clear error message
    
    Args:
        action: Any action request (ignored)
        authority: Global Authority (checked but always denied)
        
    Raises:
        ExecutionError: Always raised with message
                       "Automation disabled in current system version"
    """
    raise ExecutionError("Automation disabled in current system version")
```

### Scenario Runner

**Scenario Data Structure:**
```python
@dataclass
class Scenario:
    name: str
    inputs: StateInputs  # Decision Core inputs
    expected: ExpectedOutput  # Expected results for validation
```

**Expected Output Structure:**
```python
@dataclass
class ExpectedOutput:
    state: str  # Expected system state
    planning: str  # Expected planning permission
    execution: str  # Expected execution permission
    mode: str  # Expected authority mode
```

**Core Functions:**
```python
def load_scenarios(filepath: str) -> List[Scenario]:
    """Load scenarios from YAML or JSON file."""

def run_scenario(scenario: Scenario, config: Config) -> ScenarioResult:
    """
    Run a single scenario through the system.
    
    Steps:
    1. Evaluate state using Decision Core
    2. Derive Global Authority
    3. Check Planning Engine response
    4. Format output
    
    Returns:
        ScenarioResult with all outputs
    """

def format_scenario_output(scenario: Scenario, result: ScenarioResult) -> str:
    """
    Format scenario output in strict format:
    
    SCENARIO: {name}
    STATE: {state}
    AUTHORITY:
    - planning: {ALLOWED|DENIED}
    - execution: {ALLOWED|DENIED}
    MODE: {mode}
    ACTIVE RULES:
    - {rule1}
    - {rule2}
    """
```

## Data Models

### Configuration Extension

Extend existing `config.yaml` with authority derivation rules:

```yaml
# Existing Decision Core configuration
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
    - "Pause non-essential work"
  STRESSED:
    - "Warning: approaching overload"
    - "Discourage new projects"

# New PLO configuration
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
    execution: DENIED  # Always denied in this version
    mode: NORMAL
```

### Scenario File Format

```yaml
scenarios:
  - name: "Sudden Load Spike"
    inputs:
      fixed_deadlines_14d: 4
      active_high_load_domains: 3
      energy_scores_last_3_days: [2, 2, 2]
    expected:
      state: OVERLOADED
      planning: DENIED
      execution: DENIED
      mode: CONTAINMENT

  - name: "Normal Operation"
    inputs:
      fixed_deadlines_14d: 1
      active_high_load_domains: 1
      energy_scores_last_3_days: [4, 4, 5]
    expected:
      state: NORMAL
      planning: ALLOWED
      execution: DENIED
      mode: NORMAL

  - name: "Gradual Stress"
    inputs:
      fixed_deadlines_14d: 3
      active_high_load_domains: 2
      energy_scores_last_3_days: [3, 3, 3]
    expected:
      state: STRESSED
      planning: DENIED
      execution: DENIED
      mode: CONTAINMENT

  - name: "Recovery Transition"
    inputs:
      fixed_deadlines_14d: 1
      active_high_load_domains: 2
      energy_scores_last_3_days: [4, 4, 4]
    expected:
      state: NORMAL
      planning: ALLOWED
      execution: DENIED
      mode: NORMAL
```

### Advisory Scenario File Format

```yaml
advisory_scenarios:
  - name: "Deadline Clustering"
    inputs:
      fixed_deadlines_14d: 1
      active_high_load_domains: 1
      energy_scores_last_3_days: [4, 4, 5]
      tasks:
        - name: "ML Homework 3"
          deadline: "2026-02-12"
          type: "coursework"
        - name: "Org meeting prep"
          deadline: "2026-02-11"
          type: "admin"
        - name: "Internship deliverable"
          deadline: "2026-02-13"
          type: "work"
      constraints:
        max_parallel_focus: 2
        no_work_after: "22:00"
    expected:
      state: NORMAL
      planning: ALLOWED
      advisory_contains:
        - "3 deadlines"
        - "3-day window"
        - "Cognitive load"

  - name: "Blocked Advisory"
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
      blocked_reason: "Planning forbidden by Decision Core"
```

## Advisory Output Format

The Planning Advisor produces structured, plain-text output that is descriptive (not prescriptive), coarse-grained (not detailed), and reversible (not binding).

### Format Specification

```
PLANNING ADVISORY:
- {observation 1}
- {observation 2}
- Recommendation:
  • {suggestion 1}
  • {suggestion 2}
```

### Example Output (Allowed State)

```
PLANNING ADVISORY:
- 3 deadlines fall within a 3-day window (Feb 11-13)
- Cognitive load likely exceeds safe threshold
- This week exceeds your usual load
- Recommendation:
  • Treat coursework as primary focus
  • Minimize administrative scope
  • Avoid adding optional tasks this week
```

### Example Output (Denied State)

```
ADVICE BLOCKED
Reason: Planning forbidden by Decision Core
```

### Output Characteristics

**Descriptive Language:**
- "3 deadlines fall within a 3-day window" (observation)
- "Cognitive load likely exceeds safe threshold" (assessment)
- "This week exceeds your usual load" (comparison)

**Non-Prescriptive Language:**
- "Treat coursework as primary focus" (suggestion, not command)
- "Consider deferring non-essential tasks" (recommendation, not schedule)
- "Minimize administrative scope" (guidance, not optimization)

**Forbidden Language:**
- ❌ "Schedule homework at 2pm" (prescriptive)
- ❌ "Maximize efficiency by..." (optimization)
- ❌ "You must complete X before Y" (binding)
- ❌ "Fit task into 30-minute slot" (detailed scheduling)

### Analysis Rules

**Deadline Clustering:**
- Detect when N deadlines fall within M-day window
- Report: "{N} deadlines fall within a {M}-day window"
- Threshold: 3+ deadlines within 3 days = cluster

**Cognitive Load:**
- Compare task count to max_parallel_focus constraint
- Report: "Cognitive load likely exceeds safe threshold" when exceeded
- Report: "This week exceeds your usual load" when above normal

**Prioritization:**
- Identify task types (coursework, work, admin)
- Suggest treating urgent/important as "primary focus"
- Suggest minimizing scope of lower-priority tasks
- Suggest avoiding optional tasks during high-load periods

**Conflicts:**
- Detect overlapping deadlines
- Detect constraint violations
- Report: "Multiple high-priority tasks overlap"
- Report: "Task load exceeds max_parallel_focus constraint"

## Error Handling

### Authority Violation Errors

**Planning Denied Error:**
- When: Planning Engine called with DENIED permission
- Response: Return `PlanResult(advisory=None, reason="ADVICE BLOCKED\nReason: Planning forbidden by Decision Core", blocked_by="Decision Core")`
- Do NOT raise exception (graceful degradation)
- Do NOT provide any analysis or suggestions

**Execution Attempted Error:**
- When: Any execution function called
- Response: Raise `ExecutionError("Automation disabled in current system version")`
- Fail loudly (safety violation)

### Input Validation Errors

**Invalid Task Input:**
- Check for required fields: name, deadline, type
- Validate deadline format (ISO date: YYYY-MM-DD)
- Provide clear error: "Invalid task: missing {field}" or "Invalid deadline format"
- Return error in PlanResult reason field

**Invalid Constraint Input:**
- Validate constraint values (e.g., max_parallel_focus > 0)
- Validate time format (HH:MM for no_work_after)
- Provide clear error: "Invalid constraint: {details}"
- Return error in PlanResult reason field

### Configuration Errors

**Missing Authority Configuration:**
- Check for `authority_derivation` section in config
- Provide clear error: "Configuration missing authority_derivation section"
- Exit with non-zero status code

**Invalid Scenario File:**
- Validate scenario structure on load
- Provide clear error: "Scenario file invalid: {details}"
- List missing required fields

### Scenario Validation Errors

**Expected vs Actual Mismatch:**
- Compare scenario expected output with actual output
- Report mismatches clearly
- Continue running remaining scenarios
- Exit with non-zero status if any scenario fails

## Testing Strategy

The system will be tested using both unit tests and property-based tests to ensure correctness across all possible inputs and scenarios.

### Unit Testing Approach

Unit tests will focus on:
- **Authority derivation**: Verify correct permissions for each state
- **Planning Engine interface**: Test denial and not-implemented responses
- **Execution Layer**: Verify ExecutionError is always raised
- **Scenario loading**: Test valid and invalid scenario files
- **Scenario execution**: Test each predefined scenario
- **Output formatting**: Verify strict format compliance

### Property-Based Testing Approach

Property-based tests will verify universal properties across randomized inputs using Hypothesis (Python PBT library).

Configuration:
- Minimum 100 iterations per property test
- Each test tagged with: **Feature: personal-life-orchestrator, Property {N}: {description}**

The property tests will validate the correctness properties defined in the next section.



## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: Global Authority Completeness

*For any* valid Decision Core output, the derived Global_Authority object should contain all required fields: planning_permission (ALLOWED or DENIED), execution_permission (ALLOWED or DENIED), authority_mode (NORMAL, CONTAINMENT, or RECOVERY), state, and active_rules.

**Validates: Requirements 1.1, 1.2, 1.3, 1.4**

### Property 2: Non-NORMAL States Deny Planning

*For any* inputs that result in STRESSED or OVERLOADED state, the Global_Authority should set planning_permission to DENIED and authority_mode to CONTAINMENT.

**Validates: Requirements 1.5, 1.6**

### Property 3: NORMAL State Allows Planning

*For any* inputs that result in NORMAL state, the Global_Authority should set planning_permission to ALLOWED and authority_mode to NORMAL.

**Validates: Requirements 1.7**

### Property 4: Execution Always Denied

*For any* inputs and any system state, the Global_Authority should always set execution_permission to DENIED in this system version.

**Validates: Requirements 1.8**

### Property 5: Planning Engine Checks Authority

*For any* PlanRequest, the Planning Engine should check the Global_Authority planning_permission before proceeding.

**Validates: Requirements 2.2, 4.1**

### Property 6: Planning Denied Returns None

*For any* PlanRequest where planning_permission is DENIED, the Planning Engine should return PlanResult with plan=None and reason="Planning blocked by Decision Core".

**Validates: Requirements 2.3, 2.4, 4.3**

### Property 7: Planning Allowed Returns Not Implemented

*For any* PlanRequest where planning_permission is ALLOWED, the Planning Engine should return PlanResult with plan=None and reason="Planning interface not yet implemented".

**Validates: Requirements 2.5**

### Property 8: Execution Always Raises Error

*For any* execution request, the Execution Layer should raise ExecutionError with message "Automation disabled in current system version".

**Validates: Requirements 3.2, 3.3, 4.2, 4.4**

### Property 9: Scenario Runner Derives Authority

*For any* valid scenario, the Scenario Runner should provide inputs to Decision Core and derive Global_Authority from the output.

**Validates: Requirements 5.2, 5.3**

### Property 10: Scenario Output Completeness

*For any* scenario run, the output should contain scenario name, system state, planning permission, execution permission, authority mode, and active rules.

**Validates: Requirements 5.4, 5.5, 5.6, 5.7, 5.8**

### Property 11: Scenario Output Format Compliance

*For any* scenario run, the output should follow the strict format: "SCENARIO: {name}", "STATE: {state}", "AUTHORITY:", "- planning: {permission}", "- execution: {permission}", "MODE: {mode}", "ACTIVE RULES:", followed by rule list.

**Validates: Requirements 6.1, 6.2, 6.3, 6.4**

### Property 12: Scenario Output Consistency

*For any* two scenarios, the output format structure should be identical (same sections in same order), differing only in values.

**Validates: Requirements 6.5**

### Property 13: Scenario Output Conciseness

*For any* scenario output, it should not contain verbose explanations or unnecessary text beyond the required format sections.

**Validates: Requirements 5.9, 6.6**

### Property 14: Configuration Error Reporting

*For any* invalid configuration (missing sections, malformed YAML, missing required keys), the system should report a clear error message indicating what is wrong.

**Validates: Requirements 7.5**

### Property 15: Scenario Expected Output Validation

*For any* scenario with expected output defined, running the scenario should produce actual output that matches the expected state, planning permission, execution permission, and mode.

**Validates: Requirements 10.5**

### Property 16: CLI Output to Stdout

*For any* CLI command execution, all results should be written to stdout (not stderr, unless error).

**Validates: Requirements 11.4**

### Property 17: Task Input Validation

*For any* task input, the Planning Advisor should validate that all required fields (name, deadline, type) are present and properly formatted, returning clear error messages for invalid inputs.

**Validates: Requirements 13.2, 13.6, 13.7**

### Property 18: Authority Blocking

*For any* PlanRequest where planning_permission is DENIED, the Planning Advisor should return a blocked message containing "ADVICE BLOCKED" and "Planning forbidden by Decision Core", with no advisory content provided.

**Validates: Requirements 14.1, 14.2, 14.3, 14.4**

### Property 19: Deadline Clustering Detection

*For any* task set where 3 or more deadlines fall within a 3-day window, the Planning Advisor should flag deadline clustering and report the number of deadlines and the time window.

**Validates: Requirements 15.1, 15.2, 15.3**

### Property 20: No Prescriptive Language

*For any* advisory output, it should not contain prescriptive language (specific time scheduling, optimization commands, binding directives) and should use only descriptive, suggestive language.

**Validates: Requirements 15.5, 16.4, 16.5, 20.1, 20.4, 20.5**

### Property 21: Cognitive Load Detection

*For any* task set where the task count exceeds the max_parallel_focus constraint, the Planning Advisor should flag cognitive overload and report that load exceeds safe thresholds.

**Validates: Requirements 16.1, 16.2, 18.2**

### Property 22: Prioritization Suggestions

*For any* task set with multiple tasks, the Planning Advisor should provide prioritization suggestions that identify primary focus areas and suggest minimizing scope of lower-priority tasks.

**Validates: Requirements 17.1, 17.2, 17.3**

### Property 23: Conflict Detection

*For any* task set with overlapping deadlines or constraint violations, the Planning Advisor should warn about conflicts and clearly identify the specific conflict without resolving it automatically.

**Validates: Requirements 18.1, 18.3, 18.4**

### Property 24: Input Immutability

*For any* PlanRequest, calling the Planning Advisor should not modify the input task definitions or constraints.

**Validates: Requirements 18.5**

### Property 25: Advisory Output Format

*For any* non-blocked advisory output, it should start with "PLANNING ADVISORY:", use bullet points for observations, use nested bullets for recommendations, and contain only plain text without formatting codes.

**Validates: Requirements 19.1, 19.2, 19.3, 19.4**

### Example-Based Tests

The following requirements are best validated through specific examples rather than properties:

- **Planning Engine Interface Existence** (Requirement 2.1): Verify `propose_plan` function exists with correct signature
- **Execution Layer Module Existence** (Requirement 3.1): Verify execution module exists as placeholder
- **Scenario File Loading** (Requirement 5.1): Test loading valid YAML and JSON scenario files
- **Configuration Loading** (Requirements 7.1, 7.2): Test loading valid configuration with all sections
- **Configuration Validation** (Requirement 7.4): Test with missing sections and malformed YAML
- **Required Scenarios Exist** (Requirements 10.1, 10.2, 10.3, 10.4): Verify scenario file contains all required scenarios
- **CLI Commands Exist** (Requirements 11.1, 11.2, 11.3): Test each CLI command works
- **CLI Exit Codes** (Requirement 11.5): Test success (0) and error (non-zero) exit codes
- **Documentation Exists** (Requirements 12.1, 12.2, 12.3, 12.4, 12.5): Verify README and documentation contain required sections
- **Constraint Support** (Requirements 13.4, 13.5): Test that max_parallel_focus and time boundary constraints are accepted
- **No Execution Calls** (Requirement 20.3): Verify Planning Advisor doesn't call execution layer
- **Advisory Scenario Support** (Requirements 21.1, 21.2, 21.3, 21.4, 21.5): Test scenario runner with advisory scenarios

### Edge Cases

Property-based test generators should include these edge cases:
- Inputs at exact threshold boundaries (e.g., exactly 3 deadlines)
- All three energy scores identical
- Zero values for deadlines and domains
- Empty active rules list (NORMAL state)
- Very large input values
- Scenarios with minimal vs maximal rule lists
- Configuration with empty rule lists
- Empty task lists
- Single task scenarios
- Tasks with identical deadlines
- Tasks with deadlines exactly 3 days apart (boundary of clustering)
- Constraints with zero or negative values
- Tasks with invalid date formats
- Tasks with missing fields
- Very long task names or types
- Tasks with deadlines in the past
- Tasks with deadlines far in the future



## Error Handling (Continued)

### Layer Boundary Errors

**L0 to L1 Communication:**
- Global Authority must always be derivable from Decision Core output
- If Decision Core fails, propagate error up (don't attempt authority derivation)
- Never assume default authority values

**L1 Planning Denial:**
- When planning is denied, return graceful response (not exception)
- Always include clear reason in response
- Log denial for audit purposes (future enhancement)

**L2 Execution Prohibition:**
- Always raise ExecutionError (never silent failure)
- Error message must be explicit about prohibition
- No fallback or degraded execution mode

### Scenario Execution Errors

**Scenario Load Failures:**
- Invalid YAML/JSON: Report parse error with line number
- Missing required fields: List all missing fields
- Invalid field values: Report which field and why invalid

**Scenario Execution Failures:**
- Decision Core error: Report which scenario failed and why
- Authority derivation error: Report state that caused failure
- Output formatting error: Report which section failed

**Scenario Validation Failures:**
- Expected vs actual mismatch: Report all differences
- Continue with remaining scenarios (don't abort)
- Collect all failures and report at end

## Testing Strategy (Continued)

### Dual Testing Approach

The system requires both unit tests and property-based tests:

- **Unit tests**: Verify specific examples, edge cases, CLI commands, configuration loading, documentation existence
- **Property tests**: Verify universal properties across all inputs, authority derivation rules, output format consistency

Both are complementary and necessary for comprehensive coverage. Unit tests catch concrete bugs in specific scenarios, while property tests verify general correctness across the input space.

### Property-Based Testing Configuration

- **Library**: Hypothesis (Python)
- **Iterations**: Minimum 100 per property test
- **Tagging**: Each test must include comment: **Feature: personal-life-orchestrator, Property {N}: {property_text}**
- **Generators**: Custom generators for StateInputs, Scenarios, Configurations
- **Shrinking**: Enable Hypothesis shrinking to find minimal failing examples

### Test Organization

```
tests/
├── test_authority.py          # Properties 1-4 (authority derivation)
├── test_planning_engine.py    # Properties 5-7 (planning interface)
├── test_execution_layer.py    # Property 8 (execution prohibition)
├── test_scenario_runner.py    # Properties 9-13, 15 (scenario execution)
├── test_configuration.py      # Property 14 (config validation)
├── test_cli.py                # Property 16, CLI examples
├── test_integration.py        # End-to-end scenario tests
└── test_documentation.py      # Documentation existence tests
```

### Integration Testing

Beyond unit and property tests, integration tests will:
- Run complete scenarios end-to-end
- Verify Decision Core → Authority → Planning/Execution flow
- Test CLI commands with real scenario files
- Validate output format against expected format
- Ensure all layers respect authority boundaries

### Test Data

**Scenario Test Files:**
- `scenarios/test_scenarios.yaml`: All required scenarios for testing
- `scenarios/invalid_scenarios.yaml`: Malformed scenarios for error testing
- `scenarios/edge_cases.yaml`: Boundary condition scenarios

**Configuration Test Files:**
- `configs/test_config.yaml`: Valid configuration for testing
- `configs/invalid_config.yaml`: Missing sections for error testing
- `configs/minimal_config.yaml`: Minimal valid configuration

## Implementation Notes

### Preserving Decision Core

The existing Decision Core (PL-DSS) must remain unchanged:
- Do NOT modify `evaluator.py`, `rules.py`, `recovery.py`
- Do NOT change Decision Core interfaces
- Do NOT add L1/L2 awareness to Decision Core
- Decision Core should work independently

### New Modules to Create

1. **`authority.py`**: Global Authority derivation
2. **`planning.py`**: Planning Engine interface (L1)
3. **`execution.py`**: Execution Layer prohibition (L2)
4. **`scenario_runner.py`**: Scenario loading and execution
5. **`cli.py`**: CLI commands for PLO operations

### Configuration Extension

Extend `config.yaml` without breaking existing Decision Core:
- Add `authority_derivation` section
- Keep existing `thresholds` and `downgrade_rules` sections
- Ensure backward compatibility with existing PL-DSS

### CLI Design

New CLI commands (separate from existing PL-DSS CLI):
```bash
# Run single scenario
python -m pl_dss.plo scenario run --name "Sudden Load Spike"

# Run all scenarios
python -m pl_dss.plo scenario run-all

# Evaluate current state with authority
python -m pl_dss.plo evaluate --deadlines 4 --domains 3 --energy 2 3 2

# Validate scenario file
python -m pl_dss.plo scenario validate --file scenarios.yaml
```

### Output Format Specification

Strict format for scenario output (no deviations):
```
SCENARIO: {scenario_name}
STATE: {NORMAL|STRESSED|OVERLOADED}
AUTHORITY:
- planning: {ALLOWED|DENIED}
- execution: {ALLOWED|DENIED}
MODE: {NORMAL|CONTAINMENT|RECOVERY}
ACTIVE RULES:
- {rule1}
- {rule2}
...
```

Empty rules section when no rules active:
```
ACTIVE RULES:
(none)
```

### Future Expansion Path

This design explicitly prepares for future phases:

**Phase 2 (Future): Planning Implementation**
- Implement scheduling algorithms in Planning Engine
- Add task and constraint data structures
- Implement conflict detection
- Still respect Global Authority (no planning when denied)

**Phase 3 (Future): Controlled Execution**
- Enable execution only when explicitly safe
- Implement execution hooks with safety checks
- Add execution audit logging
- Maintain authority enforcement

**Phase 4 (Future): Full Autonomy**
- Autonomous planning and execution
- Self-monitoring and adjustment
- Advanced recovery strategies
- Always respect Decision Core authority

The current implementation (Phase 1) creates the foundation for these future phases while maintaining strict safety boundaries.

