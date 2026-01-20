# Implementation Plan: GitHub Interface Integration

## Overview

This implementation plan transforms the Personal Life Orchestrator into a daily-usable GitHub-based system while preserving strict safety guarantees. The approach follows a sequential build: freeze current state → create GitHub interface files → implement glue script → integrate Planning Engine (optional) → validate immutability.

## Tasks

- [-] 1. Freeze current system state as v0.3-stable
  - Create git tag marking the frozen state
  - Document baseline file hashes for frozen components
  - _Requirements: 1.1, 1.5_

- [ ] 2. Update README with stability notice and constitution
  - Add Stability Notice section documenting the freeze
  - Add System Constitution section with immutable rules
  - Add GitHub Interface usage instructions
  - _Requirements: 1.2, 1.3, 1.4, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6_

- [ ] 3. Create GitHub Issue template
  - [ ] 3.1 Create .github/ISSUE_TEMPLATE/life_checkin.yaml file
    - Define structured form with required fields (deadlines, domains, energy)
    - Add optional tasks field for future Planning Engine integration
    - Configure automatic labeling and title prefix
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8_

  - [ ]* 3.2 Write unit test for Issue template structure
    - Verify file exists at correct path
    - Verify required fields are configured correctly
    - Verify label and title configuration
    - _Requirements: 2.1, 2.8_

- [ ] 4. Implement Issue body parser
  - [ ] 4.1 Create scripts/run_from_issue.py with parse_issue_body() function
    - Parse GitHub Issue template format (### headers)
    - Extract deadlines, domains, energy fields
    - Extract optional tasks field
    - Handle whitespace and formatting variations
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.6_

  - [ ] 4.2 Implement parsing validation
    - Validate required fields present
    - Validate integer formats for deadlines and domains
    - Validate energy format (3 comma-separated integers, 1-5 range)
    - Return clear error messages for invalid inputs
    - _Requirements: 4.5, 4.7, 11.1, 11.2, 11.3, 11.4_

  - [ ]* 4.3 Write property test for parsing completeness
    - **Property 2: Issue Body Parsing Completeness**
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4**

  - [ ]* 4.4 Write property test for parsing error handling
    - **Property 3: Parsing Error Handling**
    - **Validates: Requirements 4.5, 11.1, 11.2, 11.3, 11.4, 16.1, 16.2**

  - [ ]* 4.5 Write property test for energy validation
    - **Property 4: Energy Score Validation**
    - **Validates: Requirements 4.7, 11.3, 11.4**

- [ ] 5. Checkpoint - Verify parsing works correctly
  - Test parser with sample Issue bodies
  - Ensure all error cases handled
  - Ensure validation reuses Decision Core logic

- [ ] 6. Implement glue script main flow
  - [ ] 6.1 Implement main() function in scripts/run_from_issue.py
    - Read Issue body from command-line argument
    - Parse Issue body into StateInputs
    - Load configuration using existing load_config()
    - Call Decision Core pipeline (evaluate_state, derive_authority, check_recovery)
    - Format output using existing format_output()
    - Print to stdout for GitHub Actions capture
    - _Requirements: 5.2, 5.3, 5.4, 5.5, 5.6, 5.9, 18.2_

  - [ ] 6.2 Implement error handling in glue script
    - Catch parsing errors and format for GitHub
    - Catch validation errors from Decision Core
    - Catch system errors and include traceback
    - Format all errors with clear user guidance
    - _Requirements: 16.1, 16.2, 16.4, 16.5_

  - [ ]* 6.3 Write property test for Decision Core pipeline execution
    - **Property 5: Decision Core Pipeline Execution**
    - **Validates: Requirements 5.2, 5.3, 5.4, 5.5**

  - [ ]* 6.4 Write property test for output determinism
    - **Property 6: Output Format Determinism**
    - **Validates: Requirements 5.6, 6.8, 18.1, 18.3**

  - [ ]* 6.5 Write property test for output completeness
    - **Property 7: Output Completeness**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5, 6.6**

  - [ ]* 6.6 Write property test for output plainness
    - **Property 8: Output Format Plainness**
    - **Validates: Requirements 6.7**

- [ ] 7. Checkpoint - Verify glue script works standalone
  - Test glue script with sample inputs
  - Verify output matches CLI format exactly
  - Ensure all error cases handled gracefully

- [ ] 8. Create GitHub Actions workflow
  - [ ] 8.1 Create .github/workflows/life_orchestrator.yml file
    - Configure trigger on Issue opened/edited with "life-checkin" label
    - Set up Python 3.13 environment on ubuntu-latest
    - Install dependencies from requirements.txt
    - Run glue script with Issue body
    - Capture output and post as Issue comment
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.9, 12.1, 12.2, 12.4, 12.5, 15.1, 15.2_

  - [ ] 8.2 Configure workflow permissions and safety
    - Set minimal permissions (issues: write, contents: read)
    - Ensure no repository modification steps
    - Ensure no external API calls
    - _Requirements: 3.7, 3.8, 14.1, 14.2, 14.3, 14.4, 14.5_

  - [ ]* 8.3 Write unit tests for workflow configuration
    - Verify workflow file exists at correct path
    - Verify trigger configuration
    - Verify Python version and environment
    - Verify no repository modification steps
    - _Requirements: 3.1, 3.2, 3.3, 3.9, 14.1, 14.2, 14.3, 14.4_

- [ ] 9. Implement comment formatting
  - [ ] 9.1 Add format_for_github() function to glue script
    - Wrap output in markdown code block
    - Preserve deterministic format
    - Handle error messages appropriately
    - _Requirements: 13.3, 13.4, 11.6_

  - [ ]* 9.2 Write property test for comment format preservation
    - **Property 17: Comment Format Preservation**
    - **Validates: Requirements 13.3, 13.4**

- [ ] 10. Test authority enforcement
  - [ ]* 10.1 Write property test for planning denial
    - **Property 9: Authority Enforcement - Planning Denial**
    - **Validates: Requirements 7.1, 7.2, 7.4**

  - [ ]* 10.2 Write property test for planning allowance
    - **Property 10: Authority Enforcement - Planning Allowance**
    - **Validates: Requirements 7.3, 7.4**

  - [ ]* 10.3 Write property test for authority check precedence
    - **Property 11: Authority Check Precedence**
    - **Validates: Requirements 7.4, 7.5**

- [ ] 11. Test execution layer prohibition
  - [ ]* 11.1 Write property test for execution prohibition
    - **Property 15: Execution Layer Prohibition**
    - **Validates: Requirements 9.1, 9.2, 9.4**

  - [ ]* 11.2 Write unit test for execution documentation
    - Verify execution.py contains clear prohibition documentation
    - Verify README documents execution is disabled
    - _Requirements: 9.3, 9.5_

- [ ] 12. Checkpoint - Verify complete pipeline
  - Create test Issue manually
  - Verify workflow triggers correctly
  - Verify comment posted with correct format
  - Verify output matches CLI for same inputs

- [ ] 13. Implement Planning Engine integration (optional)
  - [ ] 13.1 Extend glue script to handle tasks field
    - Parse tasks from Issue body
    - Pass tasks to Planning Engine when planning is ALLOWED
    - Suppress agent output when planning is DENIED
    - _Requirements: 8.7, 7.1, 7.2_

  - [ ] 13.2 Format Planning Engine output
    - Add "NON-BINDING" labels to advisory output
    - Add note about Decision Core authority
    - Append to base system output
    - _Requirements: 8.5, 8.6_

  - [ ]* 13.3 Write property tests for Planning Engine integration
    - **Property 12: Planning Engine Analysis (When Allowed)**
    - **Validates: Requirements 8.1, 8.2, 8.3, 8.4**

  - [ ]* 13.4 Write property test for Planning Engine output labeling
    - **Property 13: Planning Engine Output Labeling**
    - **Validates: Requirements 8.5, 8.6**

  - [ ]* 13.5 Write property test for Planning Engine authority respect
    - **Property 14: Planning Engine Authority Respect**
    - **Validates: Requirements 8.7**

- [ ] 14. Prepare for future agent integration
  - [ ] 14.1 Document agent integration pattern in code comments
    - Add comments showing how to integrate agents
    - Document authority enforcement requirements
    - Document output labeling requirements
    - _Requirements: 19.1, 19.5_

  - [ ]* 14.2 Write property tests for agent authority enforcement
    - **Property 20: Agent Authority Enforcement**
    - **Validates: Requirements 19.2, 19.4**

  - [ ]* 14.3 Write property test for agent output labeling
    - **Property 21: Agent Output Labeling**
    - **Validates: Requirements 19.3**

- [ ] 15. Validate immutability guarantees
  - [ ]* 15.1 Write property test for frozen component immutability
    - **Property 1: Frozen Component Immutability**
    - **Validates: Requirements 1.5, 17.1, 17.2, 17.3, 17.4, 17.5**

  - [ ]* 15.2 Write unit tests for code reuse
    - Verify glue script imports existing functions
    - Verify no duplication of Decision Core logic
    - Verify config.yaml used (not hardcoded values)
    - _Requirements: 5.7, 5.8, 11.5, 18.4_

- [ ] 16. Write integration tests
  - [ ]* 16.1 Write end-to-end integration test
    - Test complete pipeline: parse → evaluate → format → output
    - Test with NORMAL, STRESSED, OVERLOADED scenarios
    - Verify output format correctness
    - _Requirements: 20.5_

  - [ ]* 16.2 Write CLI-GitHub consistency test
    - **Property 19: CLI-GitHub Output Consistency**
    - **Validates: Requirements 18.1**

  - [ ]* 16.3 Write error handling integration tests
    - Test parsing errors end-to-end
    - Test validation errors end-to-end
    - Test system errors end-to-end
    - _Requirements: 16.3_

- [ ] 17. Create test data and examples
  - [ ] 17.1 Create sample Issue bodies for testing
    - Valid Issue (NORMAL state)
    - Valid Issue (OVERLOADED state)
    - Invalid Issue (missing field)
    - Invalid Issue (bad energy format)
    - _Requirements: 20.2, 20.3_

  - [ ] 17.2 Document testing procedures
    - Document how to test glue script standalone
    - Document how to test with sample Issues
    - Document how to verify immutability
    - _Requirements: 20.1, 20.4_

- [ ] 18. Final validation and deployment
  - [ ] 18.1 Run all tests and verify passing
    - Run unit tests
    - Run property-based tests
    - Run integration tests
    - Verify all frozen components unchanged

  - [ ] 18.2 Create deployment checklist
    - Verify git tag created
    - Verify README updated
    - Verify all files in correct locations
    - Verify workflow permissions correct

  - [ ] 18.3 Test with real GitHub Issue
    - Create test Issue in repository
    - Verify workflow triggers
    - Verify comment posted correctly
    - Verify output format matches expectations

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and configuration
- Integration tests validate end-to-end pipeline
- Task 13 (Planning Engine integration) is optional and can be deferred
- Task 14 (Agent integration preparation) is optional and can be deferred
