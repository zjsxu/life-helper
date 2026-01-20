# Implementation Plan: Personal Life Orchestrator (PLO)

## Overview

This implementation plan extends the existing Decision Core (PL-DSS) with layered authority and strict control boundaries. The implementation adds Global Authority derivation (L0→L1/L2), Planning Engine interface (L1), Execution Layer prohibition (L2), and scenario-based demonstration. All tasks preserve the existing Decision Core without modification.

## Tasks

- [x] 1. Create Global Authority module
  - [x] 1.1 Implement authority data structure and derivation
    - Create `pl_dss/authority.py` with `GlobalAuthority` dataclass
    - Implement `derive_authority()` function that maps Decision Core output to authority
    - Map OVERLOADED → planning: DENIED, mode: CONTAINMENT
    - Map STRESSED → planning: DENIED, mode: CONTAINMENT
    - Map NORMAL → planning: ALLOWED, mode: NORMAL
    - Always set execution: DENIED in this version
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8_
  
  - [ ] 1.2 Write property test for authority completeness
    - **Property 1: Global Authority Completeness**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4**
  
  - [ ] 1.3 Write property test for non-NORMAL states deny planning
    - **Property 2: Non-NORMAL States Deny Planning**
    - **Validates: Requirements 1.5, 1.6**
  
  - [ ] 1.4 Write property test for NORMAL state allows planning
    - **Property 3: NORMAL State Allows Planning**
    - **Validates: Requirements 1.7**
  
  - [ ] 1.5 Write property test for execution always denied
    - **Property 4: Execution Always Denied**
    - **Validates: Requirements 1.8**

- [x] 2. Create Planning Engine interface (L1)
  - [x] 2.1 Implement Planning Engine module
    - Create `pl_dss/planning.py` with `PlanRequest` and `PlanResult` dataclasses
    - Implement `propose_plan()` function interface
    - Check Global Authority planning_permission
    - Return None + "Planning blocked by Decision Core" when DENIED
    - Return None + "Planning interface not yet implemented" when ALLOWED
    - Do NOT implement scheduling, calendar modification, or optimization
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8_
  
  - [x] 2.2 Implement Planning Advisor data structures
    - Add `Task` dataclass with name, deadline, type fields
    - Add `Constraint` dataclass with max_parallel_focus and no_work_after fields
    - Add `AdvisoryOutput` dataclass with observations, recommendations, warnings fields
    - Update `PlanRequest` to use Task and Constraint types
    - Update `PlanResult` to include advisory field
    - _Requirements: 13.1, 13.2, 13.3_
  
  - [x] 2.3 Implement task input validation
    - Write `validate_task()` function to check required fields
    - Validate deadline format (ISO date: YYYY-MM-DD)
    - Return clear error messages for invalid inputs
    - _Requirements: 13.2, 13.6, 13.7_
  
  - [x] 2.4 Implement deadline clustering analysis
    - Write `analyze_deadline_clustering()` function
    - Detect when 3+ deadlines fall within 3-day window
    - Return observations with deadline count and time window
    - Use descriptive language only
    - _Requirements: 15.1, 15.2, 15.3, 15.4_
  
  - [x] 2.5 Implement cognitive load assessment
    - Write `assess_cognitive_load()` function
    - Compare task count to max_parallel_focus constraint
    - Return observations about load exceeding thresholds
    - Use risk-flagging language
    - _Requirements: 16.1, 16.2, 16.3_
  
  - [x] 2.6 Implement prioritization suggestions
    - Write `suggest_prioritization()` function
    - Identify task types and urgency
    - Return recommendations for primary focus and scope minimization
    - Use recommendation language, not commands
    - _Requirements: 17.1, 17.2, 17.3, 17.4_
  
  - [x] 2.7 Implement conflict detection
    - Write `detect_conflicts()` function
    - Detect overlapping deadlines
    - Detect constraint violations
    - Return warnings that identify conflicts without resolving them
    - _Requirements: 18.1, 18.2, 18.3, 18.4_
  
  - [x] 2.8 Update propose_plan with advisory logic
    - Check Global Authority and return blocked message if DENIED
    - Call validation, analysis, and suggestion functions when ALLOWED
    - Format output as AdvisoryOutput
    - Ensure no prescriptive language (no time scheduling, optimization, binding directives)
    - Ensure input immutability (don't modify tasks or constraints)
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 15.5, 16.4, 16.5, 18.5, 20.1, 20.2, 20.3, 20.4, 20.5, 20.6, 20.7_
  
  - [x] 2.9 Implement advisory output formatting
    - Write `format_advisory_output()` function
    - Start with "PLANNING ADVISORY:"
    - Use bullet points (-) for observations
    - Use nested bullets (•) for recommendations
    - Ensure plain text without formatting codes
    - _Requirements: 19.1, 19.2, 19.3, 19.4, 19.5_
  
  - [ ] 2.10 Write property test for task input validation
    - **Property 17: Task Input Validation**
    - **Validates: Requirements 13.2, 13.6, 13.7**
  
  - [ ] 2.11 Write property test for authority blocking
    - **Property 18: Authority Blocking**
    - **Validates: Requirements 14.1, 14.2, 14.3, 14.4**
  
  - [ ] 2.12 Write property test for deadline clustering detection
    - **Property 19: Deadline Clustering Detection**
    - **Validates: Requirements 15.1, 15.2, 15.3**
  
  - [ ] 2.13 Write property test for no prescriptive language
    - **Property 20: No Prescriptive Language**
    - **Validates: Requirements 15.5, 16.4, 16.5, 20.1, 20.4, 20.5**
  
  - [ ] 2.14 Write property test for cognitive load detection
    - **Property 21: Cognitive Load Detection**
    - **Validates: Requirements 16.1, 16.2, 18.2**
  
  - [ ] 2.15 Write property test for prioritization suggestions
    - **Property 22: Prioritization Suggestions**
    - **Validates: Requirements 17.1, 17.2, 17.3**
  
  - [ ] 2.16 Write property test for conflict detection
    - **Property 23: Conflict Detection**
    - **Validates: Requirements 18.1, 18.3, 18.4**
  
  - [ ] 2.17 Write property test for input immutability
    - **Property 24: Input Immutability**
    - **Validates: Requirements 18.5**
  
  - [ ] 2.18 Write property test for advisory output format
    - **Property 25: Advisory Output Format**
    - **Validates: Requirements 19.1, 19.2, 19.3, 19.4**
  
  - [x] 2.19 Write unit tests for planning advisor
    - Test constraint support (max_parallel_focus, time boundaries)
    - Test that Planning Advisor doesn't call execution layer
    - _Requirements: 13.4, 13.5, 20.3_
  
  - [ ] 2.20 Write property test for planning engine checks authority
    - **Property 5: Planning Engine Checks Authority**
    - **Validates: Requirements 2.2, 4.1**
  
  - [ ] 2.21 Write property test for planning denied returns None
    - **Property 6: Planning Denied Returns None**
    - **Validates: Requirements 2.3, 2.4, 4.3**
  
  - [ ] 2.22 Write property test for planning allowed returns advisory
    - **Property 7: Planning Allowed Returns Advisory**
    - **Validates: Requirements 2.5**
  
  - [x] 2.23 Write unit test for planning engine interface
    - Test function exists with correct signature
    - Test with DENIED authority
    - Test with ALLOWED authority
    - _Requirements: 2.1_

- [x] 3. Create Execution Layer prohibition (L2)
  - [x] 3.1 Implement Execution Layer module
    - Create `pl_dss/execution.py` with `ExecutionError` exception class
    - Implement `execute_action()` placeholder function
    - Always raise ExecutionError with message "Automation disabled in current system version"
    - Add module docstring documenting that execution is forbidden
    - Do NOT implement any automation functionality
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [ ] 3.2 Write property test for execution always raises error
    - **Property 8: Execution Always Raises Error**
    - **Validates: Requirements 3.2, 3.3, 4.2, 4.4**
  
  - [x] 3.3 Write unit test for execution layer
    - Test module exists
    - Test ExecutionError is raised
    - Test error message is correct
    - _Requirements: 3.1_

- [x] 4. Checkpoint - Ensure layer modules tested
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4.5 Checkpoint - Ensure Planning Advisor implementation complete
  - Ensure all Planning Advisor functions implemented
  - Ensure advisory output format is correct
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Create Scenario Runner
  - [x] 5.1 Implement scenario data structures
    - Create `pl_dss/scenario_runner.py` with `Scenario` and `ExpectedOutput` dataclasses
    - Define scenario file format (YAML/JSON)
    - _Requirements: 5.1_
  
  - [x] 5.2 Implement scenario loading
    - Write `load_scenarios()` function to load from YAML/JSON files
    - Validate scenario structure
    - Handle file not found and parse errors
    - _Requirements: 5.1_
  
  - [x] 5.3 Implement scenario execution
    - Write `run_scenario()` function
    - Provide inputs to Decision Core (evaluate_state)
    - Derive Global Authority from Decision Core output
    - Collect all outputs (state, authority, rules)
    - _Requirements: 5.2, 5.3_
  
  - [x] 5.4 Add advisory scenario support
    - Update scenario data structures to support task and constraint inputs
    - Update `run_scenario()` to call Planning Advisor when tasks are present
    - Include advisory output in scenario results
    - _Requirements: 21.1, 21.2_
  
  - [ ] 5.5 Write property test for scenario runner derives authority
    - **Property 9: Scenario Runner Derives Authority**
    - **Validates: Requirements 5.2, 5.3**
  
  - [x] 5.6 Implement scenario output formatting
    - Write `format_scenario_output()` function
    - Follow strict format: SCENARIO, STATE, AUTHORITY, MODE, ACTIVE RULES
    - Use consistent formatting across all scenarios
    - Do not include verbose explanations
    - _Requirements: 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_
  
  - [x] 5.7 Update output formatting for advisory scenarios
    - Include advisory output in formatted results when present
    - Format advisory output according to specification
    - _Requirements: 19.1, 19.2, 19.3, 19.4_
  
  - [ ] 5.8 Write property test for scenario output completeness
    - **Property 10: Scenario Output Completeness**
    - **Validates: Requirements 5.4, 5.5, 5.6, 5.7, 5.8**
  
  - [ ] 5.9 Write property test for scenario output format compliance
    - **Property 11: Scenario Output Format Compliance**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4**
  
  - [ ] 5.10 Write property test for scenario output consistency
    - **Property 12: Scenario Output Consistency**
    - **Validates: Requirements 6.5**
  
  - [ ] 5.11 Write property test for scenario output conciseness
    - **Property 13: Scenario Output Conciseness**
    - **Validates: Requirements 5.9, 6.6**
  
  - [x] 5.12 Implement scenario validation
    - Write `validate_scenario_output()` function
    - Compare expected vs actual outputs
    - Report mismatches clearly
    - _Requirements: 10.5_
  
  - [ ] 5.13 Write property test for scenario expected output validation
    - **Property 15: Scenario Expected Output Validation**
    - **Validates: Requirements 10.5**

- [x] 6. Extend configuration
  - [x] 6.1 Update configuration schema
    - Extend `config.yaml` with `authority_derivation` section
    - Define authority rules for each state (NORMAL, STRESSED, OVERLOADED)
    - Maintain backward compatibility with existing Decision Core config
    - _Requirements: 7.1, 7.2_
  
  - [x] 6.2 Implement configuration validation
    - Update `pl_dss/config.py` to validate authority_derivation section
    - Check for required keys and valid values
    - Report clear errors for invalid configuration
    - _Requirements: 7.4, 7.5_
  
  - [ ] 6.3 Write property test for configuration error reporting
    - **Property 14: Configuration Error Reporting**
    - **Validates: Requirements 7.5**
  
  - [x] 6.4 Write unit tests for configuration
    - Test loading valid configuration with authority_derivation
    - Test missing authority_derivation section
    - Test invalid authority values
    - _Requirements: 7.1, 7.2, 7.4_

- [x] 7. Checkpoint - Ensure configuration and scenarios tested
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Create scenario files
  - [x] 8.1 Create test scenarios file
    - Create `scenarios/test_scenarios.yaml` with all required scenarios
    - Include "Sudden Load Spike" (OVERLOADED)
    - Include "Gradual Stress" (STRESSED)
    - Include "Normal Operation" (NORMAL)
    - Include "Recovery Transition" (NORMAL after stress)
    - Define expected outputs for each scenario
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [x] 8.2 Add advisory scenarios to test file
    - Add "Deadline Clustering" scenario with 3 tasks in 3-day window
    - Add "Cognitive Overload" scenario with tasks exceeding max_parallel_focus
    - Add "Blocked Advisory" scenario with OVERLOADED state
    - Define expected advisory outputs for each scenario
    - _Requirements: 21.1, 21.2, 21.3, 21.4, 21.5_
  
  - [x] 8.3 Write unit tests for required scenarios
    - Test that all required scenarios exist in file
    - Test that each scenario has expected outputs
    - Test that advisory scenarios exist
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 21.3, 21.4, 21.5_

- [x] 9. Create CLI interface
  - [x] 9.1 Implement PLO CLI module
    - Create `pl_dss/plo_cli.py` with CLI commands
    - Implement `scenario run` command (run single scenario)
    - Implement `scenario run-all` command (run all scenarios)
    - Implement `evaluate` command (evaluate with authority)
    - Implement `scenario validate` command (validate scenario file)
    - Output results to stdout
    - Use appropriate exit codes (0 for success, non-zero for errors)
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_
  
  - [ ] 9.2 Write property test for CLI output to stdout
    - **Property 16: CLI Output to Stdout**
    - **Validates: Requirements 11.4**
  
  - [x] 9.3 Write unit tests for CLI commands
    - Test each CLI command exists and works
    - Test exit codes for success and error cases
    - _Requirements: 11.1, 11.2, 11.3, 11.5_

- [x] 10. Create documentation
  - [x] 10.1 Update README with PLO information
    - Add section explaining PLO layered architecture
    - Explain what the system does (authority enforcement)
    - Explain what the system refuses to do (unsafe automation)
    - Explain how it will expand safely (future phases)
    - Document layer responsibilities (L0, L1, L2)
    - Document authority derivation rules
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_
  
  - [x] 10.2 Write unit tests for documentation
    - Test README exists and contains required sections
    - Test layer responsibilities are documented
    - Test authority derivation rules are documented
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [x] 11. Integration testing
  - [x] 11.1 Write integration tests
    - Test complete flow: Decision Core → Authority → Planning/Execution
    - Test scenario runner end-to-end
    - Test CLI commands with real scenario files
    - Test all layers respect authority boundaries
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 8.1, 8.2, 8.3, 8.4_

- [x] 12. Final checkpoint - Complete system validation
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- All core implementation tasks are complete
- Remaining tasks are property-based tests and unit tests for comprehensive validation
- Advisory scenario support (tasks 5.4, 5.7) needs implementation to complete the Planning Advisor feature
- Each property test should run minimum 100 iterations
- Preserve existing Decision Core - do NOT modify evaluator.py, rules.py, recovery.py
- All new modules are in `pl_dss/` directory
- Use Hypothesis for property-based testing
- Tag each property test with: **Feature: personal-life-orchestrator, Property {N}: {description}**
- Focus on safety-first design - fail loudly when boundaries are violated
- Keep implementation boring and conservative - no "smart" behavior

