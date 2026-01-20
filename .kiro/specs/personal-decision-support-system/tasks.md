# Implementation Plan: Personal Decision-Support System (PL-DSS)

## Overview

This implementation plan breaks down the PL-DSS into discrete coding tasks. The system will be implemented in Python with a focus on simplicity, clarity, and deterministic behavior. All tasks build incrementally, with testing integrated throughout to catch errors early.

## Tasks

- [x] 1. Set up project structure and configuration
  - Create directory structure: `pl_dss/` with `__init__.py`, `main.py`, `evaluator.py`, `rules.py`, `recovery.py`
  - Create `config.yaml` with all thresholds, downgrade rules, and recovery advice
  - Create `README.md` with project description, what it does NOT do, and usage instructions
  - Set up testing framework (pytest) and create `tests/` directory
  - _Requirements: 4.1, 4.2, 4.3, 4.5, 7.2, 7.3, 7.4_

- [x] 2. Implement configuration loading
  - [x] 2.1 Create configuration loader function
    - Write function to load and parse YAML configuration file
    - Define configuration data structures (dataclasses or TypedDict)
    - Validate configuration structure and required keys
    - _Requirements: 4.1, 4.2, 4.3, 4.5_
  
  - [ ]* 2.2 Write unit tests for configuration loading
    - Test loading valid YAML configuration
    - Test error handling for missing file
    - Test error handling for malformed YAML
    - Test error handling for missing required keys
    - _Requirements: 4.4_

- [x] 3. Implement State Evaluator
  - [x] 3.1 Create input validation functions
    - Write function to validate energy_scores_last_3_days (exactly 3 values, range 1-5)
    - Write function to validate fixed_deadlines_14d (non-negative integer)
    - Write function to validate active_high_load_domains (non-negative integer)
    - Return clear error messages for invalid inputs
    - _Requirements: 1.5, 1.6, 7.5_
  
  - [ ]* 3.2 Write property test for input validation
    - **Property 2: Input Validation Rejects Invalid Data**
    - **Validates: Requirements 1.5, 1.6, 7.5**
  
  - [x] 3.3 Implement state evaluation logic
    - Write function to compute average of energy scores
    - Write function to count how many conditions are met
    - Write function to determine state (NORMAL/STRESSED/OVERLOADED) based on condition count
    - Generate explanation of which conditions were met
    - _Requirements: 1.1, 1.2, 1.3, 1.4_
  
  - [ ]* 3.4 Write property test for state determination
    - **Property 1: State Determination Correctness**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4**
  
  - [ ]* 3.5 Write unit tests for state evaluator
    - Test state with 0 conditions met (NORMAL)
    - Test state with 1 condition met (STRESSED)
    - Test state with 2 conditions met (OVERLOADED)
    - Test state with 3 conditions met (OVERLOADED)
    - Test boundary cases (values exactly at thresholds)
    - _Requirements: 1.2, 1.3, 1.4_

- [x] 4. Checkpoint - Ensure state evaluator tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement Emergency Rule Engine
  - [x] 5.1 Create rule lookup function
    - Write function to retrieve downgrade rules for given state from configuration
    - Return empty list for NORMAL state
    - Return configured rules without modification for STRESSED/OVERLOADED
    - _Requirements: 2.1, 2.2, 2.3, 2.5_
  
  - [ ]* 5.2 Write property test for rule engine
    - **Property 3: Rule Engine Returns Correct Rules**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.5**
  
  - [ ]* 5.3 Write unit tests for rule engine
    - Test NORMAL state returns empty rules
    - Test STRESSED state returns configured STRESSED rules
    - Test OVERLOADED state returns configured OVERLOADED rules
    - Test rules are returned exactly as configured
    - _Requirements: 2.1, 2.2, 2.3_

- [x] 6. Implement Recovery Monitor
  - [x] 6.1 Create recovery evaluation function
    - Write function to check if all recovery conditions are met
    - Generate explanation when recovery is possible
    - Identify and list blocking conditions when recovery is not possible
    - _Requirements: 3.1, 3.2, 3.3_
  
  - [ ]* 6.2 Write property test for recovery conditions
    - **Property 4: Recovery Conditions Evaluated Correctly**
    - **Validates: Requirements 3.1**
  
  - [ ]* 6.3 Write property test for recovery explanations
    - **Property 5: Recovery Explanations Are Complete**
    - **Validates: Requirements 3.2, 3.3**
  
  - [ ]* 6.4 Write unit tests for recovery monitor
    - Test recovery when all conditions met
    - Test recovery blocked by each individual condition
    - Test recovery blocked by multiple conditions
    - Test explanation content
    - _Requirements: 3.1, 3.2, 3.3_

- [x] 7. Checkpoint - Ensure all core modules tested
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Implement main controller and CLI
  - [x] 8.1 Create main orchestration function
    - Write function to load configuration
    - Write function to accept inputs (CLI arguments or prompts)
    - Call evaluator, rule engine, and recovery monitor in sequence
    - Handle errors gracefully with clear messages
    - _Requirements: 5.1, 5.2, 5.3, 5.4_
  
  - [x] 8.2 Implement output formatting
    - Write function to format state result with explanation
    - Write function to format active rules list
    - Write function to format recovery status
    - Ensure output is plain text suitable for CLI
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [ ]* 8.3 Write property test for output completeness
    - **Property 6: Output Contains Required Information**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4**
  
  - [ ]* 8.4 Write property test for output format
    - **Property 7: Output Is Plain Text**
    - **Validates: Requirements 5.5**
  
  - [ ]* 8.5 Write unit tests for main controller
    - Test end-to-end flow with various input combinations
    - Test error handling for invalid configuration
    - Test error handling for invalid inputs
    - _Requirements: 4.4, 7.5_

- [x] 9. Implement determinism verification
  - [x]* 9.1 Write property test for deterministic behavior
    - **Property 8: Deterministic Behavior**
    - **Validates: Requirements 6.2**

- [x] 10. Final integration and validation
  - [x] 10.1 Create sample configuration file
    - Populate config.yaml with realistic thresholds and rules
    - Add comments explaining each section
    - _Requirements: 4.1, 4.2, 4.3_
  
  - [x] 10.2 Test complete system manually
    - Run system with various input scenarios
    - Verify output format and clarity
    - Verify execution time is under 1 minute
    - _Requirements: 5.5, 7.1_
  
  - [x] 10.3 Verify README completeness
    - Ensure README explains what system does
    - Ensure README explains what system does NOT do
    - Ensure README explains weekly usage pattern
    - _Requirements: 7.2, 7.3, 7.4_

- [x] 11. Final checkpoint - Complete system validation
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests should run minimum 100 iterations each
- Core logic should remain under 100 lines (excluding comments/config)
- Focus on clarity and simplicity over cleverness
- All functions should be pure where possible (no global state)
