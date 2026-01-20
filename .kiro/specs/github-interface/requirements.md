# Requirements Document: GitHub Interface Integration

## Introduction

This specification defines the GitHub-based interface for the Personal Life Orchestrator (PALO), enabling daily-usable interaction through GitHub Issues and Actions while preserving strict safety guarantees. The system transforms GitHub Issues into Decision Core evaluations and posts deterministic responses as comments, without modifying the frozen Decision Core, Global Authority, or containment rules.

## Glossary

- **Decision_Core**: The frozen state evaluation and rule engine (evaluator.py, rules.py, recovery.py) that determines system state and active rules
- **Global_Authority**: The frozen authority derivation system (authority.py) that controls planning and execution permissions
- **GitHub_Interface**: The new integration layer consisting of Issue templates, GitHub Actions workflow, and glue script
- **Issue_Parser**: Component that extracts structured data from GitHub Issue body
- **Glue_Script**: Python script (scripts/run_from_issue.py) that bridges GitHub Actions to Decision Core
- **Planning_Engine**: The L1 layer (planning.py) that provides advisory analysis when permitted
- **Execution_Layer**: The L2 layer (execution.py) that is permanently disabled and fails loudly
- **Containment_Mode**: Authority mode where planning is DENIED due to STRESSED or OVERLOADED state
- **System_Constitution**: Immutable rules documented in README that prevent authority bypass

## Requirements

### Requirement 1: System Stability Freeze

**User Story:** As a system maintainer, I want to freeze the current system state as v0.3-stable, so that the Decision Core and Authority layer remain immutable during GitHub integration.

#### Acceptance Criteria

1. WHEN the system is tagged as v0.3-stable, THE System SHALL create a git tag marking the frozen state
2. WHEN the README is updated, THE System SHALL include a Stability Notice documenting the freeze
3. THE Stability_Notice SHALL explicitly state that Decision Core and Authority layer are frozen
4. THE Stability_Notice SHALL prohibit future features from bypassing or modifying frozen layers
5. THE System SHALL preserve all existing Decision Core logic without modification

### Requirement 2: GitHub Issue Template

**User Story:** As a user, I want to submit life check-ins through GitHub Issues, so that I can interact with the system without using the CLI.

#### Acceptance Criteria

1. WHEN a user creates a new Issue, THE GitHub_Interface SHALL provide a structured "Life Check-in" template
2. THE Issue_Template SHALL require a non-movable deadlines count (integer input)
3. THE Issue_Template SHALL require an active high-load domains count (integer input)
4. THE Issue_Template SHALL require energy scores as comma-separated values (e.g., "2,3,2")
5. THE Issue_Template SHALL provide an optional tasks/commitments textarea
6. THE Issue_Template SHALL automatically apply the "life-checkin" label
7. THE Issue_Template SHALL set the title prefix to "[Life] Check-in"
8. THE Issue_Template SHALL be located at .github/ISSUE_TEMPLATE/life_checkin.yaml

### Requirement 3: GitHub Actions Workflow

**User Story:** As a system operator, I want GitHub Actions to automatically process life check-in Issues, so that users receive deterministic responses without manual intervention.

#### Acceptance Criteria

1. WHEN a life-checkin Issue is created or edited, THE GitHub_Interface SHALL trigger the workflow
2. THE Workflow SHALL run on ubuntu-latest environment
3. THE Workflow SHALL use Python 3.13 for execution
4. THE Workflow SHALL install repository dependencies from requirements.txt
5. THE Workflow SHALL invoke the Glue_Script with Issue body content
6. THE Workflow SHALL post the Glue_Script output as an Issue comment
7. THE Workflow SHALL NOT use external APIs beyond GitHub's own API
8. THE Workflow SHALL NOT modify repository state (no commits, no file changes)
9. THE Workflow SHALL be located at .github/workflows/life_orchestrator.yml

### Requirement 4: Issue Body Parsing

**User Story:** As a system integrator, I want to parse GitHub Issue bodies into structured inputs, so that the Decision Core receives valid data.

#### Acceptance Criteria

1. WHEN the Issue_Parser receives an Issue body, THE System SHALL extract the deadlines field as an integer
2. WHEN the Issue_Parser receives an Issue body, THE System SHALL extract the domains field as an integer
3. WHEN the Issue_Parser receives an Issue body, THE System SHALL extract the energy field as a list of integers
4. WHEN the Issue_Parser receives an Issue body, THE System SHALL extract the tasks field as optional text
5. IF parsing fails for required fields, THEN THE System SHALL return a clear error message
6. THE Issue_Parser SHALL handle GitHub Issue template format (key-value pairs)
7. THE Issue_Parser SHALL validate that energy scores are comma-separated integers

### Requirement 5: Glue Script Integration

**User Story:** As a system architect, I want a glue script that bridges GitHub Actions to the Decision Core, so that the existing system logic is reused without modification.

#### Acceptance Criteria

1. THE Glue_Script SHALL be located at scripts/run_from_issue.py
2. WHEN the Glue_Script is invoked, THE System SHALL parse Issue body into StateInputs
3. WHEN the Glue_Script has valid inputs, THE System SHALL call the Decision Core evaluator
4. WHEN the Glue_Script has valid inputs, THE System SHALL call the Global Authority derivation
5. WHEN the Glue_Script has valid inputs, THE System SHALL call the Recovery monitor
6. THE Glue_Script SHALL output results in the deterministic CLI format
7. THE Glue_Script SHALL NOT modify Decision Core logic
8. THE Glue_Script SHALL NOT modify Global Authority logic
9. THE Glue_Script SHALL print output to stdout for GitHub Actions to capture

### Requirement 6: Deterministic Output Format

**User Story:** As a user, I want to receive structured, deterministic responses, so that I can understand the system state and authority decisions clearly.

#### Acceptance Criteria

1. THE System SHALL output the current state (NORMAL, STRESSED, or OVERLOADED)
2. THE System SHALL output planning permission (ALLOWED or DENIED)
3. THE System SHALL output execution permission (always DENIED)
4. THE System SHALL output the authority mode (NORMAL, CONTAINMENT, or RECOVERY)
5. THE System SHALL output active downgrade rules when applicable
6. THE System SHALL output recovery status and blocking conditions
7. THE Output SHALL use plain text without emojis or friendly language
8. THE Output SHALL be deterministic (same inputs always produce same output)

### Requirement 7: Authority Enforcement

**User Story:** As a safety engineer, I want planning advice suppressed when authority denies it, so that the system respects containment boundaries.

#### Acceptance Criteria

1. WHEN Global_Authority planning permission is DENIED, THE System SHALL NOT produce planning advice
2. WHEN Global_Authority planning permission is DENIED, THE System SHALL output "AGENT RESPONSE SUPPRESSED BY AUTHORITY"
3. WHEN Global_Authority planning permission is ALLOWED, THE System SHALL permit planning analysis
4. THE System SHALL check authority before any planning operation
5. THE System SHALL never bypass authority checks

### Requirement 8: Planning Engine Integration (Optional Phase)

**User Story:** As a user, I want the Planning Engine to analyze my tasks when permitted, so that I receive non-binding advisory output.

#### Acceptance Criteria

1. WHEN planning permission is ALLOWED and tasks are provided, THE Planning_Engine SHALL analyze deadline clustering
2. WHEN planning permission is ALLOWED and tasks are provided, THE Planning_Engine SHALL assess cognitive load
3. WHEN planning permission is ALLOWED and tasks are provided, THE Planning_Engine SHALL detect conflicts
4. WHEN planning permission is ALLOWED and tasks are provided, THE Planning_Engine SHALL suggest prioritization
5. THE Planning_Engine SHALL output advisory analysis with clear "NON-BINDING" label
6. THE Planning_Engine SHALL include a note that "Final authority remains with Decision Core"
7. IF planning permission is DENIED, THEN THE Planning_Engine SHALL NOT run

### Requirement 9: Execution Layer Safety

**User Story:** As a safety engineer, I want execution attempts to fail loudly, so that automation cannot run without explicit permission.

#### Acceptance Criteria

1. WHEN any component attempts execution, THE Execution_Layer SHALL raise ExecutionError
2. THE Execution_Layer SHALL remain disabled by design in this system version
3. THE System SHALL document that execution is structurally impossible
4. THE System SHALL provide clear error messages explaining why execution is disabled
5. THE System SHALL never modify calendars, schedules, or external systems

### Requirement 10: System Constitution Documentation

**User Story:** As a system maintainer, I want a documented constitution in the README, so that future developers understand the immutable safety boundaries.

#### Acceptance Criteria

1. THE README SHALL include a "System Constitution" section
2. THE Constitution SHALL state "Decision Core is the sole authority"
3. THE Constitution SHALL state "Authority derives exclusively from Decision Core"
4. THE Constitution SHALL state "Agents may analyze but never decide"
5. THE Constitution SHALL state "Execution is disabled by design"
6. THE Constitution SHALL state "No automation may bypass authority checks"

### Requirement 11: Input Validation

**User Story:** As a system operator, I want invalid inputs to be rejected with clear error messages, so that users can correct their Issue submissions.

#### Acceptance Criteria

1. WHEN deadlines input is not an integer, THE System SHALL return a validation error
2. WHEN domains input is not an integer, THE System SHALL return a validation error
3. WHEN energy scores are not three comma-separated integers, THE System SHALL return a validation error
4. WHEN energy scores are outside 1-5 range, THE System SHALL return a validation error
5. THE System SHALL reuse existing Decision Core validation logic
6. THE System SHALL format validation errors for GitHub Issue comments

### Requirement 12: Workflow Trigger Configuration

**User Story:** As a system operator, I want the workflow to trigger only on relevant Issue events, so that the system responds appropriately without unnecessary runs.

#### Acceptance Criteria

1. WHEN an Issue with label "life-checkin" is opened, THE Workflow SHALL trigger
2. WHEN an Issue with label "life-checkin" is edited, THE Workflow SHALL trigger
3. WHEN an Issue without label "life-checkin" is created, THE Workflow SHALL NOT trigger
4. THE Workflow SHALL filter by Issue labels to prevent false triggers
5. THE Workflow SHALL handle both Issue creation and edit events

### Requirement 13: Comment Posting

**User Story:** As a user, I want system responses posted as Issue comments, so that I can see the evaluation results directly in GitHub.

#### Acceptance Criteria

1. WHEN the Glue_Script completes successfully, THE Workflow SHALL post output as an Issue comment
2. WHEN the Glue_Script encounters an error, THE Workflow SHALL post the error message as an Issue comment
3. THE Comment SHALL preserve the deterministic output format
4. THE Comment SHALL use GitHub markdown formatting for readability
5. THE Comment SHALL be posted by the GitHub Actions bot

### Requirement 14: No Repository Modification

**User Story:** As a security engineer, I want the workflow to be read-only, so that automated processes cannot modify the repository state.

#### Acceptance Criteria

1. THE Workflow SHALL NOT create commits
2. THE Workflow SHALL NOT modify files in the repository
3. THE Workflow SHALL NOT push changes to branches
4. THE Workflow SHALL NOT create or modify tags
5. THE Workflow SHALL only read repository files and post Issue comments

### Requirement 15: Dependency Management

**User Story:** As a system operator, I want the workflow to install dependencies correctly, so that the Glue Script can import and use existing modules.

#### Acceptance Criteria

1. THE Workflow SHALL install dependencies from requirements.txt
2. THE Workflow SHALL use pip for Python package installation
3. THE Workflow SHALL ensure all pl_dss modules are importable
4. THE Workflow SHALL handle dependency installation failures gracefully
5. THE Workflow SHALL use a virtual environment or system Python as appropriate

### Requirement 16: Error Handling

**User Story:** As a user, I want clear error messages when something goes wrong, so that I can understand and fix the issue.

#### Acceptance Criteria

1. WHEN parsing fails, THE System SHALL return a descriptive error message
2. WHEN validation fails, THE System SHALL return the specific validation error
3. WHEN the Glue_Script crashes, THE Workflow SHALL capture and post the error
4. THE System SHALL distinguish between user errors and system errors
5. THE System SHALL provide actionable guidance in error messages

### Requirement 17: Immutability Guarantees

**User Story:** As a safety engineer, I want guarantees that frozen components cannot be modified, so that the safety core remains intact.

#### Acceptance Criteria

1. THE GitHub_Interface SHALL NOT modify evaluator.py logic
2. THE GitHub_Interface SHALL NOT modify rules.py logic
3. THE GitHub_Interface SHALL NOT modify authority.py logic
4. THE GitHub_Interface SHALL NOT modify recovery.py logic
5. THE GitHub_Interface SHALL NOT modify containment thresholds
6. THE GitHub_Interface SHALL only add new integration code in new files

### Requirement 18: CLI Compatibility

**User Story:** As a user, I want the GitHub interface to produce the same output as the CLI, so that behavior is consistent across interfaces.

#### Acceptance Criteria

1. WHEN the same inputs are provided via CLI and GitHub, THE System SHALL produce identical output
2. THE Glue_Script SHALL reuse the existing format_output function from main.py
3. THE System SHALL maintain deterministic behavior across interfaces
4. THE System SHALL use the same configuration file (config.yaml) for both interfaces

### Requirement 19: Agent Integration Preparation

**User Story:** As a system architect, I want the architecture to support future agent integration, so that agents can analyze tasks when planning is permitted.

#### Acceptance Criteria

1. THE System SHALL provide a clear integration point for agent analysis
2. THE System SHALL enforce that agents run only when planning is ALLOWED
3. THE System SHALL format agent output with "NON-BINDING" labels
4. THE System SHALL ensure agents cannot decide, execute, or bypass authority
5. THE System SHALL document agent integration rules in code comments

### Requirement 20: Testing and Validation

**User Story:** As a quality engineer, I want the GitHub interface to be testable, so that we can verify correct behavior before deployment.

#### Acceptance Criteria

1. THE Glue_Script SHALL be testable independently of GitHub Actions
2. THE Issue_Parser SHALL be testable with sample Issue bodies
3. THE System SHALL provide example Issue inputs for testing
4. THE System SHALL validate that frozen components remain unchanged
5. THE System SHALL include integration tests for the complete pipeline
