# Requirements Document

## Introduction

The Personal Life Orchestrator (PLO) is a safety-first personal autonomous system with layered authority and strict control boundaries. It builds upon the existing Decision Core (L0) by adding a Planning Engine interface (L1) and explicitly disabled Execution Hooks (L2). The system enforces that automation can NEVER override decision safety, with all authority derived from the Decision Core's state evaluation.

## Glossary

- **System**: The Personal Life Orchestrator (PLO)
- **Decision_Core**: L0 layer - existing PL-DSS that evaluates system state and determines authority
- **Planning_Engine**: L1 layer - provides advisory planning suggestions without scheduling or execution
- **Planning_Advisor**: Component within Planning_Engine that analyzes tasks and provides high-level advice
- **Task**: Work item with name, deadline, and type
- **Constraint**: User-defined limit on planning (e.g., max parallel tasks, time boundaries)
- **Advisory_Output**: Descriptive, non-prescriptive planning suggestions
- **Execution_Layer**: L2 layer - explicitly disabled automation layer
- **Global_Authority**: Object derived from Decision Core output that controls all downstream operations
- **Authority_Mode**: One of NORMAL, CONTAINMENT, or RECOVERY
- **Planning_Permission**: ALLOWED or DENIED based on Decision Core state
- **Execution_Permission**: ALLOWED or DENIED (always DENIED in this phase)
- **Scenario_Runner**: Component that demonstrates system behavior via predefined scenarios
- **System_State**: One of NORMAL, STRESSED, or OVERLOADED (from Decision Core)

## Requirements

### Requirement 1: Global Authority Derivation

**User Story:** As a system architect, I want all authority to be derived from the Decision Core, so that no layer can override safety decisions.

#### Acceptance Criteria

1. WHEN the Decision Core evaluates system state, THE System SHALL derive a Global_Authority object
2. THE Global_Authority SHALL contain planning_permission (ALLOWED or DENIED)
3. THE Global_Authority SHALL contain execution_permission (ALLOWED or DENIED)
4. THE Global_Authority SHALL contain authority_mode (NORMAL, CONTAINMENT, or RECOVERY)
5. WHEN System_State is OVERLOADED, THE Global_Authority SHALL set planning_permission to DENIED
6. WHEN System_State is STRESSED, THE Global_Authority SHALL set planning_permission to DENIED
7. WHEN System_State is NORMAL, THE Global_Authority SHALL set planning_permission to ALLOWED
8. THE Global_Authority SHALL always set execution_permission to DENIED in this system version

### Requirement 2: Planning Engine Interface

**User Story:** As a developer, I want a clear Planning Engine interface, so that future planning functionality can be added safely.

#### Acceptance Criteria

1. THE Planning_Engine SHALL provide a propose_plan function interface
2. WHEN propose_plan is called, THE Planning_Engine SHALL check Global_Authority planning_permission
3. WHEN planning_permission is DENIED, THE Planning_Engine SHALL return None for plan
4. WHEN planning_permission is DENIED, THE Planning_Engine SHALL return explanation "Planning blocked by Decision Core"
5. WHEN planning_permission is ALLOWED, THE Planning_Engine SHALL return explanation "Planning interface not yet implemented"
6. THE Planning_Engine SHALL NOT implement scheduling algorithms in this phase
7. THE Planning_Engine SHALL NOT modify calendars in this phase
8. THE Planning_Engine SHALL NOT optimize time usage in this phase

### Requirement 3: Execution Layer Prohibition

**User Story:** As a system architect, I want execution to be structurally impossible, so that automation cannot run unsafely.

#### Acceptance Criteria

1. THE Execution_Layer SHALL exist as a placeholder module
2. WHEN any execution function is called, THE Execution_Layer SHALL raise ExecutionError
3. THE ExecutionError message SHALL state "Automation disabled in current system version"
4. THE Execution_Layer SHALL document that execution is forbidden
5. THE Execution_Layer SHALL NOT implement any automation functionality

### Requirement 4: Authority Enforcement

**User Story:** As a system architect, I want all downstream modules to respect authority, so that safety boundaries are never violated.

#### Acceptance Criteria

1. WHEN Planning_Engine receives a request, THE Planning_Engine SHALL read Global_Authority
2. WHEN Execution_Layer receives a request, THE Execution_Layer SHALL read Global_Authority
3. WHEN planning_permission is DENIED, THE Planning_Engine SHALL refuse operation
4. WHEN execution_permission is DENIED, THE Execution_Layer SHALL refuse operation
5. THE System SHALL make Global_Authority available to all modules

### Requirement 5: Scenario-Based Demonstration

**User Story:** As a developer, I want to demonstrate system behavior via scenarios, so that correctness is provable without a GUI.

#### Acceptance Criteria

1. THE Scenario_Runner SHALL accept predefined scenarios from YAML or JSON files
2. WHEN a scenario is run, THE Scenario_Runner SHALL provide inputs to Decision Core
3. WHEN a scenario is run, THE Scenario_Runner SHALL derive Global_Authority from Decision Core output
4. WHEN a scenario is run, THE Scenario_Runner SHALL output scenario name
5. WHEN a scenario is run, THE Scenario_Runner SHALL output System_State
6. WHEN a scenario is run, THE Scenario_Runner SHALL output planning_permission
7. WHEN a scenario is run, THE Scenario_Runner SHALL output execution_permission
8. WHEN a scenario is run, THE Scenario_Runner SHALL output active downgrade rules
9. THE Scenario_Runner output SHALL be plain text without explanations unless requested

### Requirement 6: Scenario Output Format

**User Story:** As a developer, I want strict scenario output format, so that results are easily verifiable.

#### Acceptance Criteria

1. THE Scenario_Runner SHALL output "SCENARIO: {scenario_name}"
2. THE Scenario_Runner SHALL output "STATE: {system_state}"
3. THE Scenario_Runner SHALL output "AUTHORITY:" followed by planning and execution permissions
4. THE Scenario_Runner SHALL output "ACTIVE RULES:" followed by list of rules
5. THE Scenario_Runner output SHALL use consistent formatting across all scenarios
6. THE Scenario_Runner SHALL NOT include verbose explanations in default output

### Requirement 7: Configuration Contracts

**User Story:** As a developer, I want all thresholds configurable, so that system behavior can be adjusted without code changes.

#### Acceptance Criteria

1. THE System SHALL load all Decision Core thresholds from configuration
2. THE System SHALL load authority derivation rules from configuration
3. THE System SHALL NOT contain hard-coded magic numbers for thresholds
4. THE System SHALL validate configuration structure at startup
5. WHEN configuration is invalid, THE System SHALL report clear error message

### Requirement 8: Layered Architecture Preservation

**User Story:** As a system architect, I want clear layer separation, so that the system can expand safely.

#### Acceptance Criteria

1. THE Decision_Core SHALL operate independently without knowledge of L1 or L2
2. THE Planning_Engine SHALL depend only on Decision_Core output
3. THE Execution_Layer SHALL depend only on Decision_Core output
4. WHEN Decision_Core is modified, THE Planning_Engine and Execution_Layer SHALL remain unaffected
5. THE System SHALL document layer responsibilities clearly

### Requirement 9: Safety-First Design

**User Story:** As a user, I want the system to be boring and conservative, so that it never takes unsafe actions.

#### Acceptance Criteria

1. WHEN system state is unsafe, THE System SHALL deny all automation
2. THE System SHALL prefer explicit denial over implicit permission
3. THE System SHALL fail loudly when safety boundaries are violated
4. THE System SHALL NOT implement "smart" behavior without explicit permission
5. THE System SHALL document what it refuses to do

### Requirement 10: Demonstrable Correctness

**User Story:** As a developer, I want to prove system behavior via scenarios, so that correctness is verifiable.

#### Acceptance Criteria

1. THE System SHALL include scenario for sudden load spike (OVERLOADED state)
2. THE System SHALL include scenario for gradual stress increase (STRESSED state)
3. THE System SHALL include scenario for normal operation (NORMAL state)
4. THE System SHALL include scenario for recovery transition
5. WHEN scenarios are run, THE System SHALL produce expected outputs
6. THE System SHALL document expected outputs for each scenario

### Requirement 11: CLI-Based Operation

**User Story:** As a user, I want to run the system from command line, so that I can integrate it into workflows.

#### Acceptance Criteria

1. THE System SHALL provide CLI command to run single scenario
2. THE System SHALL provide CLI command to run all scenarios
3. THE System SHALL provide CLI command to evaluate current state with authority
4. THE System SHALL output results to stdout
5. THE System SHALL exit with appropriate status codes

### Requirement 12: Clear Documentation

**User Story:** As a developer, I want clear documentation, so that I understand system purpose and limitations.

#### Acceptance Criteria

1. THE System SHALL include README explaining what the system does
2. THE System SHALL include README explaining what the system refuses to do
3. THE System SHALL include README explaining how it will expand safely
4. THE System SHALL document layer responsibilities
5. THE System SHALL document authority derivation rules

### Requirement 13: Planning Advisor - Task Input

**User Story:** As a user, I want to provide tasks with deadlines and constraints, so that the advisor can analyze my workload.

#### Acceptance Criteria

1. THE Planning_Advisor SHALL accept a list of tasks as input
2. WHEN a task is provided, THE Planning_Advisor SHALL require name, deadline, and type fields
3. THE Planning_Advisor SHALL accept constraints as input
4. THE Planning_Advisor SHALL support max_parallel_focus constraint
5. THE Planning_Advisor SHALL support time boundary constraints
6. THE Planning_Advisor SHALL validate task input structure
7. WHEN task input is invalid, THE Planning_Advisor SHALL return clear error message

### Requirement 14: Planning Advisor - Authority Blocking

**User Story:** As a system architect, I want the advisor to respect authority strictly, so that it never provides advice when forbidden.

#### Acceptance Criteria

1. WHEN planning_permission is DENIED, THE Planning_Advisor SHALL return blocked message
2. THE blocked message SHALL state "ADVICE BLOCKED"
3. THE blocked message SHALL include reason "Planning forbidden by Decision Core"
4. WHEN planning_permission is DENIED, THE Planning_Advisor SHALL NOT provide any suggestions
5. WHEN planning_permission is DENIED, THE Planning_Advisor SHALL NOT analyze tasks
6. THE Planning_Advisor SHALL check Global_Authority before any analysis

### Requirement 15: Planning Advisor - Deadline Clustering Analysis

**User Story:** As a user, I want to know when deadlines cluster tightly, so that I can anticipate high-pressure periods.

#### Acceptance Criteria

1. WHEN multiple deadlines fall within a 3-day window, THE Planning_Advisor SHALL flag deadline clustering
2. THE Planning_Advisor SHALL report the number of deadlines in the cluster
3. THE Planning_Advisor SHALL report the time window of the cluster
4. THE Planning_Advisor output SHALL use descriptive language
5. THE Planning_Advisor output SHALL NOT prescribe specific actions

### Requirement 16: Planning Advisor - Cognitive Load Assessment

**User Story:** As a user, I want to know when my workload exceeds safe thresholds, so that I can make informed decisions.

#### Acceptance Criteria

1. WHEN task count exceeds max_parallel_focus constraint, THE Planning_Advisor SHALL flag cognitive overload
2. THE Planning_Advisor SHALL report when load exceeds usual threshold
3. THE Planning_Advisor output SHALL use risk-flagging language
4. THE Planning_Advisor output SHALL NOT provide optimization suggestions
5. THE Planning_Advisor output SHALL NOT schedule specific times

### Requirement 17: Planning Advisor - Task Prioritization Suggestions

**User Story:** As a user, I want high-level prioritization suggestions, so that I can decide what to focus on.

#### Acceptance Criteria

1. WHEN multiple tasks exist, THE Planning_Advisor SHALL suggest treating urgent tasks as primary focus
2. THE Planning_Advisor SHALL suggest minimizing scope of lower-priority tasks
3. THE Planning_Advisor SHALL suggest avoiding optional tasks during high-load periods
4. THE Planning_Advisor output SHALL use recommendation language
5. THE Planning_Advisor output SHALL NOT create schedules or time slots

### Requirement 18: Planning Advisor - Conflict Warnings

**User Story:** As a user, I want to be warned about potential conflicts, so that I can address them proactively.

#### Acceptance Criteria

1. WHEN tasks have overlapping deadlines, THE Planning_Advisor SHALL warn about potential conflicts
2. WHEN constraints are violated by task load, THE Planning_Advisor SHALL warn about constraint violations
3. THE Planning_Advisor output SHALL clearly identify the conflict
4. THE Planning_Advisor output SHALL NOT resolve conflicts automatically
5. THE Planning_Advisor output SHALL NOT modify task definitions

### Requirement 19: Planning Advisor - Output Format

**User Story:** As a user, I want clear, structured advisory output, so that I can quickly understand the analysis.

#### Acceptance Criteria

1. THE Planning_Advisor output SHALL start with "PLANNING ADVISORY:"
2. THE Planning_Advisor output SHALL use bullet points for observations
3. THE Planning_Advisor output SHALL use nested bullets for recommendations
4. THE Planning_Advisor output SHALL be plain text without formatting codes
5. THE Planning_Advisor output SHALL be concise and scannable

### Requirement 20: Planning Advisor - No Prescriptive Actions

**User Story:** As a system architect, I want the advisor to never take control, so that users remain in charge.

#### Acceptance Criteria

1. THE Planning_Advisor SHALL NOT schedule specific times
2. THE Planning_Advisor SHALL NOT modify calendars
3. THE Planning_Advisor SHALL NOT execute actions
4. THE Planning_Advisor SHALL NOT use optimization language
5. THE Planning_Advisor output SHALL be descriptive, not prescriptive
6. THE Planning_Advisor output SHALL be coarse-grained, not detailed
7. THE Planning_Advisor output SHALL be reversible, not binding

### Requirement 21: Planning Advisor - Scenario Integration

**User Story:** As a developer, I want to test the advisor via scenarios, so that correctness is verifiable.

#### Acceptance Criteria

1. THE Scenario_Runner SHALL support advisory scenarios with task inputs
2. WHEN an advisory scenario is run, THE Scenario_Runner SHALL output advisory analysis
3. THE Scenario_Runner SHALL include scenarios for deadline clustering
4. THE Scenario_Runner SHALL include scenarios for cognitive overload
5. THE Scenario_Runner SHALL include scenarios for blocked advice
