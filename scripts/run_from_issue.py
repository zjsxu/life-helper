#!/usr/bin/env python3
"""Glue script to bridge GitHub Issues to Decision Core.

This script parses GitHub Issue bodies and invokes the existing Decision Core
pipeline without modifying frozen components.

AGENT INTEGRATION PATTERN
==========================

This section documents how to integrate AI agents or other advisory systems
into the Personal Life Orchestrator while maintaining strict safety guarantees.

CORE PRINCIPLES (Requirements 19.1, 19.5)
------------------------------------------

1. **Decision Core is the sole authority**
   - All authority derives exclusively from Decision Core evaluation
   - Agents may analyze but NEVER decide
   - Agents may advise but NEVER execute
   - No agent may bypass authority checks

2. **Authority enforcement is mandatory**
   - Check authority BEFORE any agent operation
   - Agents run ONLY when planning permission is ALLOWED
   - Agents are suppressed when planning permission is DENIED
   - Authority checks cannot be skipped or bypassed

3. **Output must be clearly labeled**
   - All agent output must include "NON-BINDING" or "ADVISORY" labels
   - All agent output must note "Final authority remains with Decision Core"
   - Agent output must be visually distinct from Decision Core output
   - Users must understand agents cannot decide or execute


INTEGRATION PATTERN (Requirement 19.2, 19.4)
---------------------------------------------

To integrate an agent, follow this exact pattern:

```python
def run_with_agent(inputs: StateInputs, config: Config, agent_input: Optional[str]):
    # STEP 1: Always run Decision Core first (immutable)
    state_result = evaluate_state(inputs, config)
    rule_result = get_active_rules(state_result.state, config)
    recovery_result = check_recovery(inputs, state_result.state, config)
    
    # STEP 2: Derive Global Authority (immutable)
    authority = derive_authority(state_result, rule_result)
    
    # STEP 3: Format base Decision Core output (immutable)
    output = format_output(state_result, rule_result, recovery_result)
    
    # STEP 4: Check authority BEFORE running agent (CRITICAL)
    if authority.planning == "ALLOWED" and agent_input:
        # Planning is ALLOWED - agent may analyze
        agent_output = your_agent_function(agent_input, state_result, authority)
        
        # STEP 5: Label agent output as NON-BINDING (Requirement 19.3)
        output += "\\n\\nAGENT ANALYSIS (NON-BINDING):\\n"
        output += agent_output
        output += "\\n\\nNOTE: This is advisory analysis only."
        output += "\\nFinal authority remains with Decision Core."
        
    elif authority.planning == "DENIED" and agent_input:
        # Planning is DENIED - suppress agent output
        output += "\\n\\nAGENT RESPONSE SUPPRESSED BY AUTHORITY"
    
    return output
```


AUTHORITY ENFORCEMENT REQUIREMENTS (Requirement 19.2, 19.4)
------------------------------------------------------------

**CRITICAL: Authority checks are mandatory and cannot be bypassed.**

1. **Check authority before agent execution**
   ```python
   # CORRECT: Check authority first
   if authority.planning == "ALLOWED":
       agent_output = run_agent(...)
   
   # WRONG: Running agent without authority check
   agent_output = run_agent(...)  # FORBIDDEN
   ```

2. **Respect containment boundaries**
   - When state is STRESSED or OVERLOADED, planning is DENIED
   - When planning is DENIED, agents MUST NOT run
   - Containment protects users from cognitive overload
   - Bypassing containment violates system constitution

3. **Never modify authority logic**
   - authority.py is frozen and immutable
   - Agents cannot change authority decisions
   - Agents cannot override DENIED permissions
   - Agents cannot grant themselves execution permission

4. **Execution is permanently disabled**
   - Agents may analyze but NEVER execute
   - Execution Layer (execution.py) raises ExecutionError
   - No agent may modify calendars, schedules, or external systems
   - Automation is disabled by design


OUTPUT LABELING REQUIREMENTS (Requirement 19.3)
------------------------------------------------

All agent output MUST include these labels:

1. **Section header with NON-BINDING label**
   ```
   AGENT ANALYSIS (NON-BINDING):
   ```
   or
   ```
   PLANNING ENGINE ADVISORY (NON-BINDING):
   ```

2. **Clear advisory disclaimer**
   ```
   NOTE: This is advisory analysis only.
   Final authority remains with Decision Core.
   ```

3. **Visual separation from Decision Core output**
   - Agent output appears AFTER Decision Core output
   - Agent output is clearly separated (blank lines)
   - Agent output uses distinct formatting
   - Users can easily distinguish agent from core output

4. **Suppression message when denied**
   ```
   AGENT RESPONSE SUPPRESSED BY AUTHORITY
   ```


EXAMPLE AGENT INTEGRATIONS
---------------------------

**Example 1: Planning Engine (already implemented)**

The Planning Engine integration in this file demonstrates the correct pattern:

```python
if tasks_text:
    tasks = parse_tasks_text(tasks_text)
    
    if tasks:
        # Check authority BEFORE running Planning Engine
        if authority.planning == "ALLOWED":
            # Planning allowed - run analysis
            plan_request = PlanRequest(tasks=tasks, ...)
            plan_result = propose_plan(plan_request)
            
            if plan_result.advisory:
                # Format with NON-BINDING label
                advisory_text = format_advisory_output(plan_result.advisory)
                output += "\\n\\n" + advisory_text
                output += "\\n\\nNOTE: This is NON-BINDING advisory analysis."
                output += "\\nFinal authority remains with Decision Core."
        else:
            # Planning denied - suppress output
            output += "\\n\\nAGENT RESPONSE SUPPRESSED BY AUTHORITY"
```

**Example 2: Hypothetical LLM Agent**

```python
def integrate_llm_agent(inputs, config, user_query):
    # Run Decision Core first
    state_result = evaluate_state(inputs, config)
    rule_result = get_active_rules(state_result.state, config)
    recovery_result = check_recovery(inputs, state_result.state, config)
    authority = derive_authority(state_result, rule_result)
    output = format_output(state_result, rule_result, recovery_result)
    
    # Check authority before LLM
    if authority.planning == "ALLOWED" and user_query:
        # Call LLM with context
        llm_response = call_llm_api(
            query=user_query,
            state=state_result.state,
            authority=authority,
            rules=rule_result
        )
        
        # Label as NON-BINDING
        output += "\\n\\nLLM AGENT ANALYSIS (NON-BINDING):\\n"
        output += llm_response
        output += "\\n\\nNOTE: This is advisory analysis only."
        output += "\\nThe LLM cannot decide or execute actions."
        output += "\\nFinal authority remains with Decision Core."
    
    elif authority.planning == "DENIED":
        output += "\\n\\nLLM AGENT RESPONSE SUPPRESSED BY AUTHORITY"
    
    return output
```

**Example 3: Multi-Agent System**

```python
def integrate_multi_agent(inputs, config, agent_inputs):
    # Run Decision Core first
    state_result = evaluate_state(inputs, config)
    rule_result = get_active_rules(state_result.state, config)
    recovery_result = check_recovery(inputs, state_result.state, config)
    authority = derive_authority(state_result, rule_result)
    output = format_output(state_result, rule_result, recovery_result)
    
    # Check authority once for all agents
    if authority.planning == "ALLOWED":
        # Run multiple agents
        agent_outputs = []
        
        if agent_inputs.get('planning'):
            planning_output = planning_agent(agent_inputs['planning'])
            agent_outputs.append(("PLANNING AGENT", planning_output))
        
        if agent_inputs.get('scheduling'):
            scheduling_output = scheduling_agent(agent_inputs['scheduling'])
            agent_outputs.append(("SCHEDULING AGENT", scheduling_output))
        
        # Format all agent outputs with labels
        if agent_outputs:
            output += "\\n\\nMULTI-AGENT ANALYSIS (NON-BINDING):\\n"
            for agent_name, agent_output in agent_outputs:
                output += f"\\n--- {agent_name} ---\\n"
                output += agent_output
            output += "\\n\\nNOTE: All agent outputs are advisory only."
            output += "\\nAgents cannot decide or execute actions."
            output += "\\nFinal authority remains with Decision Core."
    
    elif authority.planning == "DENIED":
        output += "\\n\\nALL AGENT RESPONSES SUPPRESSED BY AUTHORITY"
    
    return output
```


FORBIDDEN PATTERNS
------------------

**DO NOT do any of the following:**

1. **Running agents without authority check**
   ```python
   # WRONG - bypasses authority
   agent_output = run_agent(...)
   output += agent_output
   ```

2. **Checking authority after agent runs**
   ```python
   # WRONG - agent already ran
   agent_output = run_agent(...)
   if authority.planning == "ALLOWED":
       output += agent_output
   ```

3. **Modifying authority decisions**
   ```python
   # WRONG - cannot override authority
   if authority.planning == "DENIED":
       authority.planning = "ALLOWED"  # FORBIDDEN
   ```

4. **Unlabeled agent output**
   ```python
   # WRONG - missing NON-BINDING label
   output += agent_output  # Users can't distinguish from core
   ```

5. **Granting execution permission**
   ```python
   # WRONG - execution is permanently disabled
   if authority.execution == "DENIED":
       authority.execution = "ALLOWED"  # FORBIDDEN
   ```

6. **Bypassing containment**
   ```python
   # WRONG - ignores containment boundaries
   if authority.planning == "DENIED":
       # Run agent anyway - FORBIDDEN
       agent_output = run_agent(...)
   ```


TESTING AGENT INTEGRATIONS
---------------------------

When adding agent integrations, ensure:

1. **Authority enforcement tests**
   - Test agent runs when planning is ALLOWED
   - Test agent is suppressed when planning is DENIED
   - Test agent cannot bypass authority checks

2. **Output labeling tests**
   - Test all agent output includes NON-BINDING labels
   - Test suppression message appears when denied
   - Test Decision Core output is not modified

3. **Immutability tests**
   - Test frozen components remain unchanged
   - Test agent cannot modify authority decisions
   - Test agent cannot grant execution permission

4. **Integration tests**
   - Test complete pipeline with agent
   - Test error handling in agent code
   - Test agent respects containment boundaries


SYSTEM CONSTITUTION
-------------------

These rules are immutable and apply to all agent integrations:

1. Decision Core is the sole authority
2. Authority derives exclusively from Decision Core
3. Agents may analyze but never decide
4. Execution is disabled by design
5. No automation may bypass authority checks

Violating these rules breaks the safety guarantees of the system.

"""

import re
import sys
from typing import Optional, Tuple

from pl_dss.authority import derive_authority
from pl_dss.config import Config, ConfigurationError, load_config
from pl_dss.evaluator import StateInputs, ValidationError, evaluate_state
from pl_dss.main import format_output
from pl_dss.planning import (
    Constraint,
    PlanRequest,
    Task,
    format_advisory_output,
    propose_plan,
)
from pl_dss.recovery import check_recovery
from pl_dss.rules import get_active_rules


class IssueParsingError(Exception):
    """Raised when Issue body parsing fails."""
    pass


def parse_issue_body(issue_body: str) -> Tuple[StateInputs, Optional[str]]:
    """Parse GitHub Issue body into StateInputs and optional tasks.
    
    Extracts structured data from GitHub Issue template format which uses
    ### headers followed by content. Handles whitespace and formatting variations.
    
    Expected format:
        ### Non-movable deadlines (next 14 days)
        
        4
        
        ### Active high-load domains
        
        3
        
        ### Energy (1–5, comma-separated)
        
        2,3,2
        
        ### Tasks / commitments
        
        Optional text...
    
    Args:
        issue_body: Raw Issue body text from GitHub
        
    Returns:
        Tuple of (StateInputs object for Decision Core, optional tasks text)
        
    Raises:
        IssueParsingError: If required fields missing or invalid format
    """
    if not issue_body or not issue_body.strip():
        raise IssueParsingError(
            "ERROR: Empty Issue body\n\n"
            "Details: Issue body is empty or contains only whitespace\n\n"
            "Action: Please fill in all required fields in the Issue template"
        )
    
    # Split by ### headers to get sections
    sections = re.split(r'###\s+', issue_body)
    
    # Build a dictionary of section_title -> content
    parsed_sections = {}
    for section in sections:
        if not section.strip():
            continue
        
        # Split on first newline to separate title from content
        lines = section.split('\n', 1)
        if len(lines) < 2:
            continue
        
        title = lines[0].strip().lower()
        content = lines[1].strip()
        
        parsed_sections[title] = content
    
    # Extract deadlines field
    deadlines = None
    for key in parsed_sections:
        if 'deadline' in key:
            try:
                deadlines = int(parsed_sections[key].strip())
            except ValueError:
                raise IssueParsingError(
                    "ERROR: Invalid deadlines format\n\n"
                    f"Details: Could not parse '{parsed_sections[key].strip()}' as an integer\n\n"
                    "Action: Please provide a valid integer for deadlines (e.g., 4)"
                )
            break
    
    if deadlines is None:
        raise IssueParsingError(
            "ERROR: Missing required field\n\n"
            "Details: Could not find 'Non-movable deadlines' field in Issue body\n\n"
            "Action: Please ensure the Issue template includes the deadlines field"
        )
    
    # Extract domains field
    domains = None
    for key in parsed_sections:
        if 'domain' in key or 'high-load' in key:
            try:
                domains = int(parsed_sections[key].strip())
            except ValueError:
                raise IssueParsingError(
                    "ERROR: Invalid domains format\n\n"
                    f"Details: Could not parse '{parsed_sections[key].strip()}' as an integer\n\n"
                    "Action: Please provide a valid integer for domains (e.g., 3)"
                )
            break
    
    if domains is None:
        raise IssueParsingError(
            "ERROR: Missing required field\n\n"
            "Details: Could not find 'Active high-load domains' field in Issue body\n\n"
            "Action: Please ensure the Issue template includes the domains field"
        )
    
    # Extract energy field
    energy = None
    for key in parsed_sections:
        if 'energy' in key:
            energy_str = parsed_sections[key].strip()
            try:
                # Parse comma-separated values
                energy_parts = [s.strip() for s in energy_str.split(',')]
                energy = [int(part) for part in energy_parts]
                
                # Validate count
                if len(energy) != 3:
                    raise IssueParsingError(
                        "ERROR: Invalid energy format\n\n"
                        f"Details: Energy must be 3 comma-separated integers, got {len(energy)} values\n\n"
                        "Action: Please provide exactly 3 energy scores separated by commas (e.g., 2,3,2)"
                    )
                
                # Validate range
                for i, score in enumerate(energy):
                    if score < 1 or score > 5:
                        raise IssueParsingError(
                            "ERROR: Energy score out of range\n\n"
                            f"Details: Energy score at position {i+1} is {score}, must be between 1 and 5\n\n"
                            "Action: Please ensure all energy scores are between 1 and 5"
                        )
                
            except ValueError as e:
                if 'invalid literal' in str(e).lower():
                    raise IssueParsingError(
                        "ERROR: Invalid energy format\n\n"
                        f"Details: Could not parse '{energy_str}' as comma-separated integers\n\n"
                        "Action: Please provide 3 comma-separated integers (e.g., 2,3,2)"
                    )
                raise
            break
    
    if energy is None:
        raise IssueParsingError(
            "ERROR: Missing required field\n\n"
            "Details: Could not find 'Energy' field in Issue body\n\n"
            "Action: Please ensure the Issue template includes the energy field"
        )
    
    # Extract optional tasks field (not used yet, but parsed for future)
    tasks = None
    for key in parsed_sections:
        if 'task' in key or 'commitment' in key:
            tasks = parsed_sections[key].strip() if parsed_sections[key].strip() else None
            break
    
    # Create StateInputs object
    state_inputs = StateInputs(
        fixed_deadlines_14d=deadlines,
        active_high_load_domains=domains,
        energy_scores_last_3_days=energy
    )
    
    return state_inputs, tasks


def format_for_github(output: str) -> str:
    """Format CLI output for GitHub Issue comment.
    
    Wraps output in markdown code block for readability while preserving
    the deterministic format from the CLI.
    
    Args:
        output: Formatted output from format_output()
        
    Returns:
        GitHub markdown formatted string
    """
    return f"```\n{output}\n```"


def parse_tasks_text(tasks_text: str) -> list[Task]:
    """Parse free-form tasks text into structured Task objects.
    
    Expected format (flexible):
        Task name due YYYY-MM-DD [type]
        Task name due YYYY-MM-DD
        Task name - YYYY-MM-DD
        
    Examples:
        ML Homework 3 due 2026-02-12 [coursework]
        Org meeting prep due 2026-02-10
        Review PR #123 - 2026-02-08 [work]
    
    Args:
        tasks_text: Free-form text from Issue body
        
    Returns:
        List of Task objects (may be empty if parsing fails)
    """
    if not tasks_text or not tasks_text.strip():
        return []
    
    tasks = []
    lines = tasks_text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Try to extract date (YYYY-MM-DD format)
        date_match = re.search(r'\b(\d{4}-\d{2}-\d{2})\b', line)
        if not date_match:
            continue
        
        deadline = date_match.group(1)
        
        # Try to extract type in brackets [type]
        type_match = re.search(r'\[([^\]]+)\]', line)
        task_type = type_match.group(1) if type_match else "general"
        
        # Extract task name (everything before "due" or "-" and the date)
        name_part = line
        # Remove the date
        name_part = name_part.replace(deadline, '')
        # Remove type if present
        if type_match:
            name_part = name_part.replace(type_match.group(0), '')
        # Remove common separators
        name_part = re.sub(r'\b(due|by|-)\b', '', name_part, flags=re.IGNORECASE)
        # Clean up whitespace
        name = name_part.strip()
        
        if name:
            tasks.append(Task(name=name, deadline=deadline, type=task_type))
    
    return tasks


def main():
    """Main entry point for glue script.
    
    Flow:
    1. Read Issue body from command-line argument
    2. Parse Issue body into StateInputs and tasks
    3. Load configuration
    4. Call Decision Core: evaluate_state()
    5. Call Authority: derive_authority()
    6. Call Recovery: check_recovery()
    7. Format output using existing format_output()
    8. If tasks provided and planning ALLOWED, call Planning Engine
    9. Print to stdout for GitHub Actions to capture
    
    Error Handling:
    - Parsing errors: Print clear error message
    - Validation errors: Print validation error from Decision Core
    - System errors: Print error with traceback
    """
    try:
        # Check for Issue body argument
        if len(sys.argv) < 2:
            print(
                "ERROR: Missing Issue body argument\n\n"
                "Usage: python scripts/run_from_issue.py \"<issue_body>\"\n\n"
                "This script is designed to be called by GitHub Actions.",
                file=sys.stderr
            )
            sys.exit(1)
        
        issue_body = sys.argv[1]
        
        # Parse Issue body
        try:
            inputs, tasks_text = parse_issue_body(issue_body)
        except IssueParsingError as e:
            # Format error for GitHub comment
            formatted_error = format_for_github(str(e))
            print(formatted_error, file=sys.stderr)
            sys.exit(1)
        
        # Load configuration
        try:
            config = load_config('config.yaml')
        except ConfigurationError as e:
            error_msg = (
                f"ERROR: Configuration error\n\n"
                f"Details: {str(e)}\n\n"
                f"Action: Please check that config.yaml exists and is valid"
            )
            formatted_error = format_for_github(error_msg)
            print(formatted_error, file=sys.stderr)
            sys.exit(1)
        
        # Run Decision Core pipeline
        try:
            state_result = evaluate_state(inputs, config)
            rule_result = get_active_rules(state_result.state, config)
            recovery_result = check_recovery(inputs, state_result.state, config)
        except ValidationError as e:
            # Format validation error for GitHub comment
            formatted_error = format_for_github(str(e))
            print(formatted_error, file=sys.stderr)
            sys.exit(1)
        
        # Derive Global Authority
        authority = derive_authority(state_result, rule_result)
        
        # Format output using existing format_output function
        output = format_output(state_result, rule_result, recovery_result)
        
        # Planning Engine integration (Requirements 8.7, 7.1, 7.2)
        if tasks_text:
            # Parse tasks from text
            tasks = parse_tasks_text(tasks_text)
            
            if tasks:
                # Check authority before running Planning Engine
                if authority.planning == "ALLOWED":
                    # Planning is allowed - run Planning Engine
                    plan_request = PlanRequest(
                        tasks=tasks,
                        constraints=Constraint(),  # Default constraints
                        decision_state=authority
                    )
                    plan_result = propose_plan(plan_request)
                    
                    if plan_result.advisory:
                        # Format and append advisory output (Requirement 8.5, 8.6)
                        advisory_text = format_advisory_output(plan_result.advisory)
                        output += "\n\n" + advisory_text
                        output += "\n\nNOTE: This is NON-BINDING advisory analysis."
                        output += "\nFinal authority remains with Decision Core."
                else:
                    # Planning is denied - suppress agent output (Requirements 7.1, 7.2)
                    output += "\n\nAGENT RESPONSE SUPPRESSED BY AUTHORITY"
        
        # Format for GitHub comment with markdown code block
        formatted_output = format_for_github(output)
        
        # Print to stdout for GitHub Actions to capture
        print(formatted_output)
        
    except KeyboardInterrupt:
        error_msg = "\n\nOperation cancelled by user."
        formatted_error = format_for_github(error_msg)
        print(formatted_error, file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        import traceback
        error_msg = (
            f"ERROR: Unexpected system error\n\n"
            f"Details: {str(e)}\n\n"
            f"Traceback:\n{traceback.format_exc()}\n\n"
            f"Action: Please report this error to the system maintainer"
        )
        formatted_error = format_for_github(error_msg)
        print(formatted_error, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
