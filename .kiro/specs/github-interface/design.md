# Design Document: GitHub Interface Integration

## Overview

The GitHub Interface Integration extends the Personal Life Orchestrator (PLO) with a production-grade GitHub-based interface, enabling daily-usable interaction through GitHub Issues and Actions while preserving strict safety guarantees. This design maintains the frozen Decision Core and Global Authority layers as immutable components, adding only a thin integration layer that bridges GitHub to the existing system.

The integration follows a safety-first architecture where:
- GitHub Issues serve as the user input interface
- GitHub Actions workflow orchestrates the evaluation pipeline
- A glue script bridges GitHub to the Decision Core without modification
- All authority enforcement and containment rules remain intact
- Execution remains permanently disabled

## Architecture

### System Layers

```
┌─────────────────────────────────────────────────────────┐
│                    GitHub Interface                      │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Issue     │  │   Workflow   │  │ Glue Script  │  │
│  │  Template   │→ │   (Actions)  │→ │ (Bridge)     │  │
│  └─────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              Existing PLO System (Frozen)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Decision    │→ │   Global     │→ │  Planning    │ │
│  │    Core      │  │  Authority   │  │   Engine     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Integration Flow

1. **User Input**: User creates GitHub Issue using structured template
2. **Trigger**: GitHub Actions workflow triggers on Issue creation/edit
3. **Parse**: Glue script parses Issue body into StateInputs
4. **Evaluate**: Glue script calls Decision Core → Authority → Recovery
5. **Format**: Glue script formats output in deterministic CLI format
6. **Respond**: Workflow posts formatted output as Issue comment

### Design Principles

1. **Immutability**: Frozen components (Decision Core, Authority) remain unchanged
2. **Reusability**: Glue script reuses existing system functions
3. **Determinism**: Same inputs always produce same outputs
4. **Safety**: Authority enforcement and execution prohibition preserved
5. **Simplicity**: Minimal integration code, maximum reuse


## Components and Interfaces

### GitHub Issue Template

**File**: `.github/ISSUE_TEMPLATE/life_checkin.yaml`

**Purpose**: Provides structured form for users to submit life check-in data

**Structure**:
```yaml
name: Life Check-in
description: Talk to the Personal Life Orchestrator
title: "[Life] Check-in"
labels: ["life-checkin"]
body:
  - type: input
    id: deadlines
    attributes:
      label: Non-movable deadlines (next 14 days)
      description: Number only
    validations:
      required: true
  
  - type: input
    id: domains
    attributes:
      label: Active high-load domains
      description: Number only
    validations:
      required: true
  
  - type: input
    id: energy
    attributes:
      label: Energy (1–5, comma-separated)
      placeholder: "2,3,2"
    validations:
      required: true
  
  - type: textarea
    id: tasks
    attributes:
      label: Tasks / commitments
      description: Optional free text
    validations:
      required: false
```

**Design Rationale**:
- Uses GitHub's native Issue form syntax for validation
- Required fields enforce data completeness
- Optional tasks field supports future Planning Engine integration
- Label "life-checkin" enables workflow filtering


### GitHub Actions Workflow

**File**: `.github/workflows/life_orchestrator.yml`

**Purpose**: Orchestrates the evaluation pipeline when Issues are created/edited

**Trigger Configuration**:
```yaml
on:
  issues:
    types: [opened, edited]
```

**Job Configuration**:
```yaml
jobs:
  evaluate:
    if: contains(github.event.issue.labels.*.name, 'life-checkin')
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Set up Python 3.13
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run evaluation
        id: evaluate
        run: |
          python scripts/run_from_issue.py "${{ github.event.issue.body }}"
      
      - name: Post comment
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '```\n' + process.env.OUTPUT + '\n```'
            })
        env:
          OUTPUT: ${{ steps.evaluate.outputs.result }}
```

**Design Rationale**:
- Label filtering prevents false triggers
- Python 3.13 ensures compatibility
- Checkout step provides access to repository code
- Dependency installation enables module imports
- Output captured and posted as markdown code block
- No repository modification (read-only workflow)


### Glue Script (Bridge Component)

**File**: `scripts/run_from_issue.py`

**Purpose**: Bridges GitHub Actions to Decision Core without modifying frozen components

**Core Functions**:

```python
def parse_issue_body(issue_body: str) -> StateInputs:
    """
    Parse GitHub Issue body into StateInputs.
    
    Extracts:
    - deadlines: integer from "Non-movable deadlines" field
    - domains: integer from "Active high-load domains" field
    - energy: list of 3 integers from "Energy" field (comma-separated)
    - tasks: optional text from "Tasks / commitments" field
    
    Args:
        issue_body: Raw Issue body text from GitHub
        
    Returns:
        StateInputs object for Decision Core
        
    Raises:
        ValueError: If required fields missing or invalid format
    """

def format_for_github(output: str) -> str:
    """
    Format CLI output for GitHub Issue comment.
    
    Wraps output in markdown code block for readability.
    Preserves deterministic format from CLI.
    
    Args:
        output: Formatted output from format_output()
        
    Returns:
        GitHub markdown formatted string
    """

def main():
    """
    Main entry point for glue script.
    
    Flow:
    1. Read Issue body from command-line argument
    2. Parse Issue body into StateInputs
    3. Load configuration
    4. Call Decision Core: evaluate_state()
    5. Call Authority: derive_authority()
    6. Call Recovery: check_recovery()
    7. Format output using existing format_output()
    8. Print to stdout for GitHub Actions to capture
    
    Error Handling:
    - Parsing errors: Print clear error message
    - Validation errors: Print validation error from Decision Core
    - System errors: Print error with traceback
    """
```

**Design Rationale**:
- Reuses existing `format_output()` from `main.py` for consistency
- Reuses existing validation from `evaluator.py` for correctness
- Minimal new code (only parsing and main flow)
- No modification of Decision Core logic
- Deterministic output identical to CLI


### Issue Body Parser

**Parsing Strategy**:

GitHub Issue templates produce body text in this format:
```
### Non-movable deadlines (next 14 days)

4

### Active high-load domains

3

### Energy (1–5, comma-separated)

2,3,2

### Tasks / commitments

ML Homework 3 due Feb 12
Org meeting prep
```

**Parsing Algorithm**:
1. Split body by `###` headers
2. Extract section title and content
3. Match section titles to field names
4. Parse content based on field type:
   - Integer fields: `int(content.strip())`
   - Energy field: `[int(x.strip()) for x in content.split(',')]`
   - Tasks field: `content.strip()` (optional)
5. Validate extracted values
6. Construct StateInputs object

**Error Handling**:
- Missing required field → `ValueError("Missing required field: {field}")`
- Invalid integer → `ValueError("Invalid integer for {field}: {value}")`
- Invalid energy format → `ValueError("Energy must be 3 comma-separated integers")`
- Energy out of range → `ValueError("Energy scores must be between 1 and 5")`


## Data Models

### StateInputs (Existing)

Reused from Decision Core without modification:

```python
@dataclass
class StateInputs:
    fixed_deadlines_14d: int
    active_high_load_domains: int
    energy_scores_last_3_days: List[int]
```

### Issue Body Structure

Logical representation of parsed Issue data:

```python
@dataclass
class IssueParsedData:
    deadlines: int
    domains: int
    energy: List[int]  # Length 3, values 1-5
    tasks: Optional[str]  # Optional free text
```

Mapping to StateInputs:
```python
StateInputs(
    fixed_deadlines_14d=parsed.deadlines,
    active_high_load_domains=parsed.domains,
    energy_scores_last_3_days=parsed.energy
)
```

### Output Format

The system produces deterministic output in this exact format:

```
=== Personal Decision-Support System ===

Current State: {NORMAL|STRESSED|OVERLOADED}
Reason: {explanation}

Active Rules:
  • {rule1}
  • {rule2}

Recovery Status: {Ready|Not ready}
{recovery explanation}
```

When posted to GitHub, wrapped in markdown code block:
````markdown
```
=== Personal Decision-Support System ===
...
```
````


## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: Frozen Component Immutability

*For any* frozen component file (evaluator.py, rules.py, authority.py, recovery.py, config.yaml thresholds), the file content should remain byte-for-byte identical to v0.3-stable tag.

**Validates: Requirements 1.5, 17.1, 17.2, 17.3, 17.4, 17.5**

### Property 2: Issue Body Parsing Completeness

*For any* valid GitHub Issue body, parsing should successfully extract all required fields (deadlines as integer, domains as integer, energy as list of 3 integers) and optional fields (tasks as string or None).

**Validates: Requirements 4.1, 4.2, 4.3, 4.4**

### Property 3: Parsing Error Handling

*For any* Issue body with missing or invalid required fields, parsing should fail with a clear error message indicating which field is problematic and why.

**Validates: Requirements 4.5, 11.1, 11.2, 11.3, 11.4, 16.1, 16.2**

### Property 4: Energy Score Validation

*For any* energy field value, the parser should validate that it contains exactly 3 comma-separated integers, each between 1 and 5, rejecting any other format with a clear error.

**Validates: Requirements 4.7, 11.3, 11.4**

### Property 5: Decision Core Pipeline Execution

*For any* valid StateInputs, the glue script should call evaluate_state(), derive_authority(), and check_recovery() in sequence, passing results between functions correctly.

**Validates: Requirements 5.2, 5.3, 5.4, 5.5**

### Property 6: Output Format Determinism

*For any* inputs, the glue script output should be deterministic (identical on repeated runs) and match the exact CLI format from format_output().

**Validates: Requirements 5.6, 6.8, 18.1, 18.3**

### Property 7: Output Completeness

*For any* inputs, the system output should contain all required fields: current state, planning permission, execution permission, authority mode, active rules (when applicable), and recovery status.

**Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5, 6.6**

### Property 8: Output Format Plainness

*For any* output, it should use plain text without emojis, excessive punctuation, or overly friendly language, maintaining a professional deterministic tone.

**Validates: Requirements 6.7**

### Property 9: Authority Enforcement - Planning Denial

*For any* inputs that result in STRESSED or OVERLOADED state, the system should set planning permission to DENIED and should NOT produce planning advice.

**Validates: Requirements 7.1, 7.2, 7.4**

### Property 10: Authority Enforcement - Planning Allowance

*For any* inputs that result in NORMAL state, the system should set planning permission to ALLOWED and should permit planning analysis (when tasks are provided).

**Validates: Requirements 7.3, 7.4**

### Property 11: Authority Check Precedence

*For any* code path that involves planning, the authority check should occur before any planning analysis, ensuring no bypass is possible.

**Validates: Requirements 7.4, 7.5**

### Property 12: Planning Engine Analysis (When Allowed)

*For any* valid task set when planning is ALLOWED, the Planning Engine should analyze deadline clustering, assess cognitive load, detect conflicts, and suggest prioritization.

**Validates: Requirements 8.1, 8.2, 8.3, 8.4**

### Property 13: Planning Engine Output Labeling

*For any* planning advisory output, it should include clear "NON-BINDING" or "ADVISORY" labels and a note that "Final authority remains with Decision Core".

**Validates: Requirements 8.5, 8.6**

### Property 14: Planning Engine Authority Respect

*For any* inputs where planning permission is DENIED, the Planning Engine should not execute analysis and should return a blocked message.

**Validates: Requirements 8.7**

### Property 15: Execution Layer Prohibition

*For any* execution attempt, the Execution Layer should raise ExecutionError with a clear message explaining that automation is disabled.

**Validates: Requirements 9.1, 9.2, 9.4**

### Property 16: Validation Error Formatting

*For any* validation error from the Decision Core, the glue script should format it appropriately for GitHub Issue comments, preserving the error message clarity.

**Validates: Requirements 11.6**

### Property 17: Comment Format Preservation

*For any* output, when posted as a GitHub Issue comment, it should preserve the deterministic format and use markdown code blocks for readability.

**Validates: Requirements 13.3, 13.4**

### Property 18: Error Message Quality

*For any* error (parsing, validation, system), the error message should distinguish between user errors and system errors, and provide actionable guidance.

**Validates: Requirements 16.4, 16.5**

### Property 19: CLI-GitHub Output Consistency

*For any* inputs, providing the same values via CLI (--deadlines, --domains, --energy) and via GitHub Issue should produce byte-for-byte identical output.

**Validates: Requirements 18.1**

### Property 20: Agent Authority Enforcement

*For any* future agent integration, agents should only execute when planning permission is ALLOWED, and should never bypass authority checks.

**Validates: Requirements 19.2, 19.4**

### Property 21: Agent Output Labeling

*For any* agent output, it should be formatted with "NON-BINDING" labels and clear indication that the agent cannot decide or execute.

**Validates: Requirements 19.3**


## Error Handling

### Parsing Errors

**Missing Required Field**:
- Error: `ValueError("Missing required field: {field_name}")`
- User Action: Add the missing field to the Issue
- Example: "Missing required field: deadlines"

**Invalid Integer Format**:
- Error: `ValueError("Invalid integer for {field}: {value}")`
- User Action: Provide a valid integer
- Example: "Invalid integer for deadlines: abc"

**Invalid Energy Format**:
- Error: `ValueError("Energy must be 3 comma-separated integers (1-5)")`
- User Action: Provide exactly 3 integers separated by commas
- Example: "Energy must be 3 comma-separated integers (1-5), got: 2,3"

**Energy Out of Range**:
- Error: `ValueError("Energy score {value} out of range (must be 1-5)")`
- User Action: Ensure all energy scores are between 1 and 5
- Example: "Energy score 6 out of range (must be 1-5)"

### Validation Errors

The glue script reuses existing Decision Core validation, which produces errors like:

```
ERROR: Invalid energy scores count
Details: Received 2 values
Expected: Energy scores must be 3 integers between 1 and 5
```

These errors are passed through unchanged to maintain consistency with CLI behavior.

### System Errors

**Configuration Load Failure**:
- Error: `ConfigurationError("Failed to load config.yaml: {reason}")`
- System Action: Exit with non-zero status
- GitHub Action: Post error comment and fail workflow

**Decision Core Failure**:
- Error: Propagate exception from Decision Core
- System Action: Print traceback to stderr
- GitHub Action: Post error comment with traceback

**Workflow Errors**:
- Dependency installation failure → Workflow fails with clear error
- Script execution failure → Workflow captures stderr and posts as comment
- Comment posting failure → Workflow fails but evaluation still logged

### Error Response Format

All errors posted to GitHub Issues follow this format:

```
ERROR: {error_type}

Details: {specific_error_message}

Action: {what_user_should_do}
```

Example:
```
ERROR: Invalid Input

Details: Energy must be 3 comma-separated integers (1-5), got: 2,3

Action: Please edit the Issue and provide exactly 3 energy scores separated by commas.
```


## Testing Strategy

The system will be tested using both unit tests and property-based tests to ensure correctness across all possible inputs and scenarios.

### Dual Testing Approach

- **Unit tests**: Verify specific examples, edge cases, file existence, configuration correctness, documentation presence
- **Property tests**: Verify universal properties across randomized inputs, authority enforcement, output consistency

Both are complementary and necessary for comprehensive coverage. Unit tests catch concrete bugs in specific scenarios, while property tests verify general correctness across the input space.

### Property-Based Testing Configuration

- **Library**: Hypothesis (Python)
- **Iterations**: Minimum 100 per property test
- **Tagging**: Each test must include comment: **Feature: github-interface, Property {N}: {property_text}**
- **Generators**: Custom generators for Issue bodies, StateInputs, invalid inputs
- **Shrinking**: Enable Hypothesis shrinking to find minimal failing examples

### Test Organization

```
tests/
├── test_github_integration.py     # Properties 2-4, 16 (parsing)
├── test_glue_script.py            # Properties 5-7, 19 (glue script)
├── test_authority_enforcement.py  # Properties 9-11, 14 (authority)
├── test_planning_integration.py   # Properties 12-13 (planning)
├── test_execution_prohibition.py  # Property 15 (execution)
├── test_agent_integration.py      # Properties 20-21 (agents)
├── test_immutability.py           # Property 1 (frozen components)
├── test_file_structure.py         # File existence tests
├── test_workflow_config.py        # Workflow configuration tests
└── test_documentation.py          # Documentation tests
```

### Unit Testing Focus

Unit tests will verify:
- **File Existence**: Issue template, workflow file, glue script exist at correct paths
- **Workflow Configuration**: Correct triggers, Python version, dependency installation
- **Template Structure**: Required fields, labels, title format
- **Documentation**: README contains System Constitution with all required statements
- **Git Tag**: v0.3-stable tag exists and points to correct commit
- **Configuration Reuse**: Glue script uses config.yaml, not hardcoded values
- **Function Reuse**: Glue script imports and uses format_output() from main.py

### Property Testing Focus

Property tests will verify:
- **Parsing Robustness**: All valid Issue bodies parse correctly
- **Error Handling**: All invalid inputs produce clear errors
- **Determinism**: Same inputs always produce same outputs
- **Authority Enforcement**: Planning denied when required, allowed when safe
- **Output Completeness**: All required fields present in output
- **Immutability**: Frozen components unchanged
- **Consistency**: CLI and GitHub produce identical outputs

### Integration Testing

End-to-end tests will:
- Create sample Issue bodies
- Run glue script with sample inputs
- Verify output format matches expected
- Test error scenarios (missing fields, invalid values)
- Verify authority enforcement in complete pipeline
- Test Planning Engine integration (when implemented)

### Test Data

**Sample Issue Bodies**:
```python
VALID_ISSUE_NORMAL = """
### Non-movable deadlines (next 14 days)

1

### Active high-load domains

1

### Energy (1–5, comma-separated)

4,4,5

### Tasks / commitments

Review PR #123
"""

VALID_ISSUE_OVERLOADED = """
### Non-movable deadlines (next 14 days)

4

### Active high-load domains

3

### Energy (1–5, comma-separated)

2,2,2
"""

INVALID_ISSUE_MISSING_FIELD = """
### Non-movable deadlines (next 14 days)

4

### Energy (1–5, comma-separated)

2,2,2
"""

INVALID_ISSUE_BAD_ENERGY = """
### Non-movable deadlines (next 14 days)

1

### Active high-load domains

1

### Energy (1–5, comma-separated)

2,3
"""
```

### Edge Cases

Property-based test generators should include:
- Boundary values (0, 1, exact thresholds)
- Maximum valid values
- Empty optional fields
- Whitespace variations in Issue bodies
- Different line ending formats (LF, CRLF)
- Unicode characters in tasks field
- Very long task descriptions
- Energy scores at boundaries (1, 5)
- Exact threshold values for state transitions


## Implementation Notes

### Preserving Frozen Components

The following files MUST NOT be modified:
- `pl_dss/evaluator.py` - Decision Core state evaluation
- `pl_dss/rules.py` - Decision Core rule engine
- `pl_dss/authority.py` - Global Authority derivation
- `pl_dss/recovery.py` - Recovery monitoring
- `config.yaml` (thresholds and downgrade_rules sections)

Any changes to these files violate the system constitution and break the safety guarantees.

### New Files to Create

1. **`.github/ISSUE_TEMPLATE/life_checkin.yaml`** - Issue template
2. **`.github/workflows/life_orchestrator.yml`** - GitHub Actions workflow
3. **`scripts/run_from_issue.py`** - Glue script (bridge component)

### Code Reuse Strategy

The glue script MUST reuse existing functions:

```python
# Import existing functions
from pl_dss.config import load_config
from pl_dss.evaluator import StateInputs, evaluate_state
from pl_dss.authority import derive_authority
from pl_dss.recovery import check_recovery
from pl_dss.main import format_output

# Use them without modification
config = load_config('config.yaml')
state_result = evaluate_state(inputs, config)
authority = derive_authority(state_result, rule_result)
recovery = check_recovery(inputs, state_result.state, config)
output = format_output(state_result, rule_result, recovery)
```

This ensures:
- Consistency with CLI behavior
- Reuse of tested validation logic
- Identical output format
- No duplication of Decision Core logic

### README Updates

Add these sections to README.md:

**Stability Notice**:
```markdown
## Stability Notice

v0.3-stable freezes the Decision Core and Authority layer. No future feature may bypass or modify these layers.

The following components are immutable:
- Decision Core (evaluator.py, rules.py, recovery.py)
- Global Authority (authority.py)
- Containment rules and thresholds
```

**System Constitution**:
```markdown
## System Constitution

- Decision Core is the sole authority.
- Authority derives exclusively from Decision Core.
- Agents may analyze but never decide.
- Execution is disabled by design.
- No automation may bypass authority checks.
```

**GitHub Interface Usage**:
```markdown
## GitHub Interface

### Creating a Life Check-in

1. Go to Issues → New Issue
2. Select "Life Check-in" template
3. Fill in required fields:
   - Non-movable deadlines (next 14 days): integer
   - Active high-load domains: integer
   - Energy (1–5, comma-separated): e.g., "2,3,2"
4. Optionally add tasks/commitments
5. Submit Issue

The system will automatically evaluate your state and post a response as a comment.

### Understanding the Response

The response includes:
- **Current State**: NORMAL, STRESSED, or OVERLOADED
- **Authority**: Planning and execution permissions
- **Mode**: NORMAL, CONTAINMENT, or RECOVERY
- **Active Rules**: Downgrade rules when in containment
- **Recovery Status**: Whether you can return to NORMAL mode
```

### Future Agent Integration

When implementing agent analysis (optional Requirement 8), follow this pattern:

```python
def run_with_agent(inputs: StateInputs, config: Config, tasks: Optional[str]):
    """Run system with optional agent analysis."""
    # Always run Decision Core first
    state_result = evaluate_state(inputs, config)
    rule_result = get_active_rules(state_result.state, config)
    authority = derive_authority(state_result, rule_result)
    recovery = check_recovery(inputs, state_result.state, config)
    
    # Format base output
    output = format_output(state_result, rule_result, recovery)
    
    # Only run agent if planning is ALLOWED
    if authority.planning == "ALLOWED" and tasks:
        agent_output = analyze_tasks(tasks)
        output += "\n\nAGENT ANALYSIS (NON-BINDING):\n"
        output += agent_output
        output += "\n\nNOTE: Final authority remains with Decision Core."
    elif authority.planning == "DENIED" and tasks:
        output += "\n\nAGENT RESPONSE SUPPRESSED BY AUTHORITY"
    
    return output
```

Key principles:
- Agent runs ONLY when planning is ALLOWED
- Agent output clearly labeled as NON-BINDING
- Authority check happens before agent execution
- Agent cannot modify authority or execute actions

### Workflow Permissions

The GitHub Actions workflow requires these permissions:

```yaml
permissions:
  issues: write  # To post comments
  contents: read  # To checkout repository
```

These are minimal permissions that:
- Allow reading repository code
- Allow posting Issue comments
- Do NOT allow modifying repository
- Do NOT allow pushing commits
- Do NOT allow creating tags

### Security Considerations

1. **Input Validation**: All Issue inputs validated before processing
2. **No Code Execution**: Issue body is data only, not executed as code
3. **Read-Only Workflow**: Cannot modify repository state
4. **Frozen Core**: Decision logic cannot be bypassed
5. **Execution Disabled**: No automation can run

### Deployment Steps

1. Create git tag: `git tag v0.3-stable && git push origin v0.3-stable`
2. Create Issue template file
3. Create workflow file
4. Create glue script
5. Update README with new sections
6. Test with sample Issues
7. Verify frozen components unchanged (file hash comparison)

### Monitoring and Validation

After deployment, verify:
- Issue template appears in New Issue menu
- Workflow triggers on Issue creation
- Comments posted successfully
- Output format matches CLI
- Frozen components unchanged (compare with v0.3-stable)
- Authority enforcement working correctly

