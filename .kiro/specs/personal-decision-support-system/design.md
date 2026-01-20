# Design Document: Personal Life Decision-Support System (PL-DSS)

## Overview

The Personal Life Decision-Support System (PL-DSS) is a minimal, deterministic CLI application that evaluates a user's current state and provides behavioral guidance to prevent overload. The system consists of three core modules: State Evaluator, Emergency Rule Engine, and Recovery Monitor. All logic is rule-based, transparent, and configurable via a single YAML configuration file.

The system is explicitly designed to be simple, local, and deterministic. It does NOT include task management, calendar integration, databases, authentication, or any external API dependencies.

## Architecture

The system follows a functional, pipeline-based architecture:

```
User Input → State Evaluator → Rule Engine → Recovery Monitor → Text Output
                    ↓              ↓              ↓
                Config File    Config File    Config File
```

### Module Responsibilities

1. **State Evaluator** (`evaluator.py`)
   - Accepts manual inputs: fixed_deadlines_14d, active_high_load_domains, energy_scores_last_3_days
   - Validates inputs
   - Applies deterministic rules to compute System_State (NORMAL, STRESSED, OVERLOADED)
   - Returns state with explanation

2. **Emergency Rule Engine** (`rules.py`)
   - Accepts System_State
   - Loads downgrade rules from configuration
   - Returns applicable rules based on state
   - No logic beyond rule lookup

3. **Recovery Monitor** (`recovery.py`)
   - Accepts current inputs and System_State
   - Evaluates recovery conditions from configuration
   - Returns recovery status with explanation
   - Identifies blocking conditions when recovery not possible

4. **Main Controller** (`main.py`)
   - Orchestrates the pipeline
   - Loads configuration
   - Handles CLI interface
   - Formats and displays output

### Configuration Structure

Single YAML file (`config.yaml`) containing:

```yaml
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
    - "Creative work reduced to minimum viable expression"
    - "Administrative work: only non-delegable tasks"
  STRESSED:
    - "Warning: approaching overload"
    - "Discourage new projects"
    - "Suggest creating time buffers"

recovery_advice:
  - "Deadlines have cleared"
  - "High-load domains have reduced"
  - "Energy levels have stabilized"
```

## Components and Interfaces

### State Evaluator

**Input Data Structure:**
```python
class StateInputs:
    fixed_deadlines_14d: int
    active_high_load_domains: int
    energy_scores_last_3_days: list[int]  # length 3, values 1-5
```

**Output Data Structure:**
```python
class StateResult:
    state: str  # "NORMAL" | "STRESSED" | "OVERLOADED"
    explanation: str
    conditions_met: list[str]
```

**Core Function:**
```python
def evaluate_state(inputs: StateInputs, config: dict) -> StateResult:
    """
    Evaluates system state based on inputs and configured thresholds.
    
    Logic:
    - Count how many conditions are true:
      1. fixed_deadlines_14d >= threshold
      2. active_high_load_domains >= threshold
      3. avg(energy_scores) <= threshold
    - If 2+ conditions true: OVERLOADED
    - If exactly 1 condition true: STRESSED
    - Otherwise: NORMAL
    """
```

**Validation:**
- energy_scores_last_3_days must have exactly 3 elements
- All energy scores must be integers 1-5 inclusive
- fixed_deadlines_14d and active_high_load_domains must be non-negative integers

### Emergency Rule Engine

**Input:**
```python
state: str  # "NORMAL" | "STRESSED" | "OVERLOADED"
```

**Output:**
```python
class RuleResult:
    active_rules: list[str]
    state: str
```

**Core Function:**
```python
def get_active_rules(state: str, config: dict) -> RuleResult:
    """
    Returns applicable downgrade rules for the given state.
    
    Simple lookup from config.downgrade_rules[state].
    Returns empty list for NORMAL state.
    """
```

### Recovery Monitor

**Input:**
```python
inputs: StateInputs
current_state: str
```

**Output:**
```python
class RecoveryResult:
    can_recover: bool
    explanation: str
    blocking_conditions: list[str]
```

**Core Function:**
```python
def check_recovery(inputs: StateInputs, current_state: str, config: dict) -> RecoveryResult:
    """
    Determines if recovery to NORMAL is possible.
    
    Recovery conditions (all must be true):
    - fixed_deadlines_14d <= recovery threshold
    - active_high_load_domains <= recovery threshold
    - avg(energy_scores) >= recovery threshold
    
    Returns explanation and list of blocking conditions if any.
    """
```

### Main Controller

**Responsibilities:**
- Parse command-line arguments or prompt for inputs
- Load and validate configuration file
- Call evaluator, rule engine, and recovery monitor in sequence
- Format output for CLI display

**Output Format:**
```
=== Personal Decision-Support System ===

Current State: OVERLOADED
Reason: 2 conditions met
  ✓ Fixed deadlines (4) >= threshold (3)
  ✓ High-load domains (3) >= threshold (3)
  ✗ Average energy (3.0) > threshold (2)

Active Rules:
  • No new commitments
  • Pause technical tool development
  • Creative work reduced to minimum viable expression
  • Administrative work: only non-delegable tasks

Recovery Status: Not ready
Blocking conditions:
  • Fixed deadlines (4) > recovery threshold (1)
  • High-load domains (3) > recovery threshold (2)
```

## Data Models

### Configuration Schema

```python
class Config:
    thresholds: ThresholdConfig
    downgrade_rules: dict[str, list[str]]
    recovery_advice: list[str]

class ThresholdConfig:
    overload: OverloadThresholds
    recovery: RecoveryThresholds

class OverloadThresholds:
    fixed_deadlines_14d: int
    active_high_load_domains: int
    avg_energy_score: int

class RecoveryThresholds:
    fixed_deadlines_14d: int
    active_high_load_domains: int
    avg_energy_score: int
```

### Input Validation Rules

1. **Energy Scores:**
   - Must be a list of exactly 3 integers
   - Each value must be in range [1, 5]
   - Error message: "Energy scores must be 3 integers between 1 and 5"

2. **Deadline Count:**
   - Must be non-negative integer
   - Error message: "Fixed deadlines must be a non-negative integer"

3. **High-Load Domains:**
   - Must be non-negative integer
   - Error message: "Active high-load domains must be a non-negative integer"

4. **Configuration File:**
   - Must exist and be valid YAML
   - Must contain all required keys
   - Error message: "Configuration file missing or invalid: {details}"

## Error Handling

### Input Validation Errors
- Validate all inputs before processing
- Return clear error messages indicating which input is invalid and why
- Exit with non-zero status code

### Configuration Errors
- Check for missing configuration file at startup
- Validate configuration structure and required keys
- Provide helpful error messages with expected format
- Exit with non-zero status code

### Runtime Errors
- Catch and handle file I/O errors
- Catch and handle YAML parsing errors
- Provide user-friendly error messages
- Never expose stack traces to end users in normal operation

### Error Message Format
```
ERROR: {brief description}
Details: {specific information}
Expected: {what should be provided}
```

## Testing Strategy

The system will be tested using both unit tests and property-based tests to ensure correctness across all possible inputs.

### Unit Testing Approach

Unit tests will focus on:
- **Specific examples**: Verify correct state transitions for known input combinations
- **Edge cases**: Test boundary values (e.g., exactly at thresholds, empty energy scores)
- **Error conditions**: Validate error handling for invalid inputs
- **Configuration loading**: Test valid and invalid configuration files
- **Integration points**: Verify correct data flow between modules

Example unit tests:
- Test state evaluation with 0, 1, 2, and 3 conditions met
- Test recovery check at exact threshold boundaries
- Test invalid energy scores (out of range, wrong count)
- Test missing configuration keys

### Property-Based Testing Approach

Property-based tests will verify universal properties across randomized inputs using a Python PBT library (e.g., Hypothesis).

Configuration:
- Minimum 100 iterations per property test
- Each test tagged with: **Feature: personal-decision-support-system, Property {N}: {description}**

The property tests will validate the correctness properties defined in the next section.



## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: State Determination Correctness

*For any* valid inputs (fixed_deadlines_14d, active_high_load_domains, energy_scores_last_3_days), the State_Evaluator should return:
- OVERLOADED when 2 or more conditions are met (deadlines >= 3, domains >= 3, avg_energy <= 2)
- STRESSED when exactly 1 condition is met
- NORMAL when 0 conditions are met

**Validates: Requirements 1.1, 1.2, 1.3, 1.4**

### Property 2: Input Validation Rejects Invalid Data

*For any* invalid input (energy scores not exactly 3 values, energy scores outside [1,5], negative deadlines, negative domains), the State_Evaluator should reject the input with a clear error message.

**Validates: Requirements 1.5, 1.6, 7.5**

### Property 3: Rule Engine Returns Correct Rules

*For any* system state and configuration, the Rule_Engine should return:
- All configured OVERLOADED rules when state is OVERLOADED
- All configured STRESSED rules when state is STRESSED  
- Empty list when state is NORMAL
- Rules exactly as defined in configuration without modification

**Validates: Requirements 2.1, 2.2, 2.3, 2.5**

### Property 4: Recovery Conditions Evaluated Correctly

*For any* valid inputs, the Recovery_Monitor should indicate recovery is possible if and only if all recovery conditions are met (deadlines <= 1, domains <= 2, avg_energy >= 4).

**Validates: Requirements 3.1**

### Property 5: Recovery Explanations Are Complete

*For any* inputs, the Recovery_Monitor should provide:
- An explanation when recovery is possible
- A list of blocking conditions when recovery is not possible
- Non-empty, informative text in both cases

**Validates: Requirements 3.2, 3.3**

### Property 6: Output Contains Required Information

*For any* valid inputs, the system output should contain:
- The current system state
- An explanation of why that state was determined
- All applicable downgrade rules (if state is STRESSED or OVERLOADED)
- Recovery status and advice (if applicable)

**Validates: Requirements 5.1, 5.2, 5.3, 5.4**

### Property 7: Output Is Plain Text

*For any* valid inputs, the system output should be plain text without markup, suitable for CLI display.

**Validates: Requirements 5.5**

### Property 8: Deterministic Behavior

*For any* valid inputs, running the system multiple times with the same inputs and configuration should produce identical output every time.

**Validates: Requirements 6.2**

### Example-Based Tests

The following requirements are best validated through specific examples rather than properties:

- **Configuration Loading** (Requirements 2.4, 3.4, 4.1, 4.2, 4.3): Test with valid YAML and JSON config files
- **Configuration Error Handling** (Requirement 4.4): Test with missing file and malformed YAML
- **Documentation** (Requirements 7.2, 7.3, 7.4): Verify README exists and contains required sections

### Edge Cases

Property-based test generators should include these edge cases:
- Energy scores at exact boundaries (1, 5)
- Thresholds at exact boundaries (e.g., deadlines exactly 3)
- Zero values for deadlines and domains
- All three energy scores identical
- Empty configuration rules
- Very large input values
