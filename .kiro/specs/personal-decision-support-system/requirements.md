# Requirements Document

## Introduction

The Personal Life Decision-Support System (PL-DSS) is a minimal, deterministic system that evaluates a user's current state (normal, stressed, or overloaded) based on manual inputs and provides pre-defined behavioral constraints to prevent collapse. The system is explicitly NOT a productivity tool, task manager, or calendar system. It exists solely to help a single user recognize when to slow down, stop, or recover.

## Glossary

- **System**: The Personal Life Decision-Support System (PL-DSS)
- **State_Evaluator**: Component that determines current system state based on inputs
- **Rule_Engine**: Component that outputs behavioral constraints based on system state
- **Recovery_Monitor**: Component that determines when safe return to normal mode is possible
- **System_State**: One of three values: NORMAL, STRESSED, or OVERLOADED
- **Fixed_Deadline**: A non-movable deadline within the next 14 days
- **High_Load_Domain**: A life domain requiring high cognitive load (e.g., work project, family crisis, health issue)
- **Energy_Score**: Subjective daily energy rating from 1 (lowest) to 5 (highest)
- **Downgrade_Rule**: Pre-defined behavioral constraint activated during STRESSED or OVERLOADED states

## Requirements

### Requirement 1: State Evaluation

**User Story:** As a user, I want the system to evaluate my current state based on manual inputs, so that I can understand whether I am operating normally, under stress, or overloaded.

#### Acceptance Criteria

1. WHEN the user provides fixed_deadlines_14d, active_high_load_domains, and energy_scores_last_3_days, THE State_Evaluator SHALL compute the System_State
2. WHEN at least two of the following conditions are true: (fixed_deadlines_14d >= 3), (active_high_load_domains >= 3), (average of energy_scores_last_3_days <= 2), THE State_Evaluator SHALL return OVERLOADED
3. WHEN exactly one of the conditions in 1.2 is true, THE State_Evaluator SHALL return STRESSED
4. WHEN none of the conditions in 1.2 are true, THE State_Evaluator SHALL return NORMAL
5. THE State_Evaluator SHALL validate that energy_scores_last_3_days contains exactly three integers between 1 and 5 inclusive
6. THE State_Evaluator SHALL validate that fixed_deadlines_14d and active_high_load_domains are non-negative integers

### Requirement 2: Emergency Rule Engine

**User Story:** As a user, I want the system to provide pre-defined behavioral constraints when I am stressed or overloaded, so that I can follow clear guidelines to prevent collapse.

#### Acceptance Criteria

1. WHEN the System_State is OVERLOADED, THE Rule_Engine SHALL output all downgrade rules configured for the OVERLOADED state
2. WHEN the System_State is STRESSED, THE Rule_Engine SHALL output all downgrade rules configured for the STRESSED state
3. WHEN the System_State is NORMAL, THE Rule_Engine SHALL output no downgrade rules
4. THE Rule_Engine SHALL load downgrade rules from a configuration file
5. WHERE downgrade rules are defined in the configuration, THE Rule_Engine SHALL apply them without modification based on System_State

### Requirement 3: Recovery Monitoring

**User Story:** As a user, I want the system to determine when I can safely return to normal mode, so that I know when recovery has been achieved.

#### Acceptance Criteria

1. WHEN fixed_deadlines_14d <= 1 AND active_high_load_domains <= 2 AND average of energy_scores_last_3_days >= 4, THE Recovery_Monitor SHALL indicate recovery is possible
2. WHEN recovery conditions are met, THE Recovery_Monitor SHALL provide an explanation of why recovery is allowed
3. WHEN recovery conditions are not met, THE Recovery_Monitor SHALL indicate which conditions are blocking recovery
4. THE Recovery_Monitor SHALL load recovery thresholds from a configuration file

### Requirement 4: Configuration Management

**User Story:** As a developer, I want all thresholds and rules defined in a configuration file, so that I can adjust system behavior without modifying code.

#### Acceptance Criteria

1. THE System SHALL load all evaluation thresholds from a configuration file
2. THE System SHALL load all downgrade rules from a configuration file
3. THE System SHALL load all recovery conditions from a configuration file
4. WHEN the configuration file is missing or invalid, THE System SHALL report a clear error message
5. THE System SHALL support YAML or JSON format for configuration

### Requirement 5: Output and Reporting

**User Story:** As a user, I want clear text output explaining my current state and applicable rules, so that I can make informed decisions.

#### Acceptance Criteria

1. WHEN the System runs, THE System SHALL output the current System_State
2. WHEN the System runs, THE System SHALL output an explanation of why the current state was determined
3. WHEN downgrade rules are active, THE System SHALL output all applicable rules
4. WHEN recovery is possible, THE System SHALL output recovery advice
5. THE System SHALL format all output as plain text suitable for CLI use

### Requirement 6: System Constraints

**User Story:** As a developer, I want the system to remain minimal and deterministic, so that it is maintainable and reliable.

#### Acceptance Criteria

1. THE System SHALL execute locally without external API calls
2. THE System SHALL use deterministic rule-based logic without AI or ML models
3. THE System SHALL implement core logic in 100 lines or fewer (excluding comments and configuration)
4. THE System SHALL use minimal dependencies (standard library preferred)
5. THE System SHALL NOT implement task management, calendar syncing, databases, authentication, notifications, web scraping, or cloud deployment
6. THE System SHALL use pure functions without global state where possible

### Requirement 7: Usability

**User Story:** As a user, I want to run the system quickly and understand its purpose immediately, so that I can integrate it into my weekly routine.

#### Acceptance Criteria

1. WHEN a user runs the System for the first time, THE System SHALL execute in less than 1 minute
2. THE System SHALL include a README that explains what the system does
3. THE System SHALL include a README that explains what the system deliberately does NOT do
4. THE System SHALL include a README that explains how to use the system weekly
5. THE System SHALL provide clear error messages when invalid inputs are provided
