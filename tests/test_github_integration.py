"""Integration tests for GitHub Interface.

Tests the complete GitHub Issue → Decision Core pipeline, including:
- End-to-end parsing and evaluation
- CLI-GitHub output consistency
- Error handling across the pipeline

These tests validate that the GitHub interface correctly bridges Issues
to the Decision Core without modifying frozen components.

Requirements: 16.3, 18.1, 20.5
"""

import subprocess
import sys
from pathlib import Path

import pytest
from hypothesis import given, strategies as st

from pl_dss.config import load_config
from pl_dss.evaluator import StateInputs, evaluate_state
from pl_dss.rules import get_active_rules
from pl_dss.authority import derive_authority
from pl_dss.recovery import check_recovery
from pl_dss.main import format_output
from scripts.run_from_issue import parse_issue_body, format_for_github, IssueParsingError


# Sample Issue bodies for testing
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

VALID_ISSUE_STRESSED = """
### Non-movable deadlines (next 14 days)

3

### Active high-load domains

2

### Energy (1–5, comma-separated)

3,3,3
"""

VALID_ISSUE_OVERLOADED = """
### Non-movable deadlines (next 14 days)

4

### Active high-load domains

3

### Energy (1–5, comma-separated)

2,2,2

### Tasks / commitments

ML Homework 3 due 2026-02-12
Org meeting prep
"""

INVALID_ISSUE_MISSING_DEADLINES = """
### Active high-load domains

3

### Energy (1–5, comma-separated)

2,2,2
"""

INVALID_ISSUE_MISSING_DOMAINS = """
### Non-movable deadlines (next 14 days)

4

### Energy (1–5, comma-separated)

2,2,2
"""

INVALID_ISSUE_MISSING_ENERGY = """
### Non-movable deadlines (next 14 days)

4

### Active high-load domains

3
"""

INVALID_ISSUE_BAD_ENERGY_FORMAT = """
### Non-movable deadlines (next 14 days)

1

### Active high-load domains

1

### Energy (1–5, comma-separated)

2,3
"""

INVALID_ISSUE_ENERGY_OUT_OF_RANGE = """
### Non-movable deadlines (next 14 days)

1

### Active high-load domains

1

### Energy (1–5, comma-separated)

2,6,3
"""

INVALID_ISSUE_BAD_DEADLINES = """
### Non-movable deadlines (next 14 days)

abc

### Active high-load domains

3

### Energy (1–5, comma-separated)

2,2,2
"""

INVALID_ISSUE_BAD_DOMAINS = """
### Non-movable deadlines (next 14 days)

4

### Active high-load domains

xyz

### Energy (1–5, comma-separated)

2,2,2
"""


# Test 16.1: End-to-end integration test
def test_end_to_end_normal_state():
    """Test complete pipeline with NORMAL state inputs.
    
    Validates: parse → evaluate → format → output
    
    Requirements: 20.5
    """
    # Parse Issue body
    inputs, tasks = parse_issue_body(VALID_ISSUE_NORMAL)
    
    # Verify parsing
    assert inputs.fixed_deadlines_14d == 1
    assert inputs.active_high_load_domains == 1
    assert inputs.energy_scores_last_3_days == [4, 4, 5]
    assert tasks is not None
    
    # Load config
    config = load_config('config.yaml')
    
    # Evaluate state
    state_result = evaluate_state(inputs, config)
    assert state_result.state == "NORMAL"
    
    # Get active rules
    rule_result = get_active_rules(state_result.state, config)
    
    # Derive authority
    authority = derive_authority(state_result, rule_result)
    assert authority.planning == "ALLOWED"
    assert authority.execution == "DENIED"
    assert authority.mode == "NORMAL"
    
    # Check recovery
    recovery_result = check_recovery(inputs, state_result.state, config)
    
    # Format output
    output = format_output(state_result, rule_result, recovery_result)
    
    # Verify output format
    assert "Personal Decision-Support System" in output
    assert "Current State: NORMAL" in output
    assert "Recovery Status: Ready" in output
    
    # Format for GitHub
    github_output = format_for_github(output)
    assert github_output.startswith("```\n")
    assert github_output.endswith("\n```")


def test_end_to_end_stressed_state():
    """Test complete pipeline with STRESSED state inputs.
    
    Validates: parse → evaluate → format → output
    
    Requirements: 20.5
    """
    # Parse Issue body
    inputs, tasks = parse_issue_body(VALID_ISSUE_STRESSED)
    
    # Verify parsing
    assert inputs.fixed_deadlines_14d == 3
    assert inputs.active_high_load_domains == 2
    assert inputs.energy_scores_last_3_days == [3, 3, 3]
    
    # Load config
    config = load_config('config.yaml')
    
    # Evaluate state
    state_result = evaluate_state(inputs, config)
    assert state_result.state == "STRESSED"
    
    # Get active rules
    rule_result = get_active_rules(state_result.state, config)
    
    # Derive authority
    authority = derive_authority(state_result, rule_result)
    assert authority.planning == "DENIED"
    assert authority.execution == "DENIED"
    assert authority.mode == "CONTAINMENT"
    
    # Check recovery
    recovery_result = check_recovery(inputs, state_result.state, config)
    
    # Format output
    output = format_output(state_result, rule_result, recovery_result)
    
    # Verify output format
    assert "Current State: STRESSED" in output
    assert "ACTIVE RULES:" in output or "Active Rules:" in output


def test_end_to_end_overloaded_state():
    """Test complete pipeline with OVERLOADED state inputs.
    
    Validates: parse → evaluate → format → output
    
    Requirements: 20.5
    """
    # Parse Issue body
    inputs, tasks = parse_issue_body(VALID_ISSUE_OVERLOADED)
    
    # Verify parsing
    assert inputs.fixed_deadlines_14d == 4
    assert inputs.active_high_load_domains == 3
    assert inputs.energy_scores_last_3_days == [2, 2, 2]
    assert tasks is not None
    
    # Load config
    config = load_config('config.yaml')
    
    # Evaluate state
    state_result = evaluate_state(inputs, config)
    assert state_result.state == "OVERLOADED"
    
    # Get active rules
    rule_result = get_active_rules(state_result.state, config)
    
    # Derive authority
    authority = derive_authority(state_result, rule_result)
    assert authority.planning == "DENIED"
    assert authority.execution == "DENIED"
    assert authority.mode == "CONTAINMENT"
    
    # Check recovery
    recovery_result = check_recovery(inputs, state_result.state, config)
    
    # Format output
    output = format_output(state_result, rule_result, recovery_result)
    
    # Verify output format
    assert "Current State: OVERLOADED" in output
    assert "ACTIVE RULES:" in output or "Active Rules:" in output


# Test 16.2: CLI-GitHub consistency test (Property 19)
@given(
    deadlines=st.integers(min_value=0, max_value=10),
    domains=st.integers(min_value=0, max_value=10),
    energy1=st.integers(min_value=1, max_value=5),
    energy2=st.integers(min_value=1, max_value=5),
    energy3=st.integers(min_value=1, max_value=5)
)
def test_cli_github_output_consistency(deadlines, domains, energy1, energy2, energy3):
    """Property 19: CLI-GitHub Output Consistency.
    
    For any inputs, providing the same values via CLI and via GitHub Issue
    should produce byte-for-byte identical output (excluding markdown wrapper).
    
    Feature: github-interface, Property 19: CLI-GitHub Output Consistency
    
    Validates: Requirements 18.1
    """
    # Create Issue body
    issue_body = f"""
### Non-movable deadlines (next 14 days)

{deadlines}

### Active high-load domains

{domains}

### Energy (1–5, comma-separated)

{energy1},{energy2},{energy3}
"""
    
    # Parse Issue body
    inputs_github, _ = parse_issue_body(issue_body)
    
    # Create inputs directly (simulating CLI)
    inputs_cli = StateInputs(
        fixed_deadlines_14d=deadlines,
        active_high_load_domains=domains,
        energy_scores_last_3_days=[energy1, energy2, energy3]
    )
    
    # Verify inputs are identical
    assert inputs_github.fixed_deadlines_14d == inputs_cli.fixed_deadlines_14d
    assert inputs_github.active_high_load_domains == inputs_cli.active_high_load_domains
    assert inputs_github.energy_scores_last_3_days == inputs_cli.energy_scores_last_3_days
    
    # Load config
    config = load_config('config.yaml')
    
    # Evaluate with GitHub inputs
    state_result_github = evaluate_state(inputs_github, config)
    rule_result_github = get_active_rules(state_result_github.state, config)
    recovery_result_github = check_recovery(inputs_github, state_result_github.state, config)
    authority_github = derive_authority(state_result_github, rule_result_github)
    output_github = format_output(state_result_github, rule_result_github, recovery_result_github)
    
    # Evaluate with CLI inputs
    state_result_cli = evaluate_state(inputs_cli, config)
    rule_result_cli = get_active_rules(state_result_cli.state, config)
    recovery_result_cli = check_recovery(inputs_cli, state_result_cli.state, config)
    authority_cli = derive_authority(state_result_cli, rule_result_cli)
    output_cli = format_output(state_result_cli, rule_result_cli, recovery_result_cli)
    
    # Verify outputs are byte-for-byte identical
    assert output_github == output_cli
    
    # Verify authority is identical
    assert authority_github.state == authority_cli.state
    assert authority_github.planning == authority_cli.planning
    assert authority_github.execution == authority_cli.execution
    assert authority_github.mode == authority_cli.mode


# Test 16.3: Error handling integration tests
def test_error_handling_missing_deadlines():
    """Test parsing error for missing deadlines field.
    
    Requirements: 16.3
    """
    with pytest.raises(IssueParsingError) as exc_info:
        parse_issue_body(INVALID_ISSUE_MISSING_DEADLINES)
    
    error_msg = str(exc_info.value)
    assert "ERROR: Missing required field" in error_msg
    assert "deadlines" in error_msg.lower()
    assert "Action:" in error_msg


def test_error_handling_missing_domains():
    """Test parsing error for missing domains field.
    
    Requirements: 16.3
    """
    with pytest.raises(IssueParsingError) as exc_info:
        parse_issue_body(INVALID_ISSUE_MISSING_DOMAINS)
    
    error_msg = str(exc_info.value)
    assert "ERROR: Missing required field" in error_msg
    assert "domain" in error_msg.lower()
    assert "Action:" in error_msg


def test_error_handling_missing_energy():
    """Test parsing error for missing energy field.
    
    Requirements: 16.3
    """
    with pytest.raises(IssueParsingError) as exc_info:
        parse_issue_body(INVALID_ISSUE_MISSING_ENERGY)
    
    error_msg = str(exc_info.value)
    assert "ERROR: Missing required field" in error_msg
    assert "energy" in error_msg.lower()
    assert "Action:" in error_msg


def test_error_handling_bad_energy_format():
    """Test parsing error for invalid energy format (wrong count).
    
    Requirements: 16.3
    """
    with pytest.raises(IssueParsingError) as exc_info:
        parse_issue_body(INVALID_ISSUE_BAD_ENERGY_FORMAT)
    
    error_msg = str(exc_info.value)
    assert "ERROR: Invalid energy format" in error_msg
    assert "3 comma-separated integers" in error_msg
    assert "Action:" in error_msg


def test_error_handling_energy_out_of_range():
    """Test parsing error for energy scores out of range.
    
    Requirements: 16.3
    """
    with pytest.raises(IssueParsingError) as exc_info:
        parse_issue_body(INVALID_ISSUE_ENERGY_OUT_OF_RANGE)
    
    error_msg = str(exc_info.value)
    assert "ERROR: Energy score out of range" in error_msg
    assert "between 1 and 5" in error_msg
    assert "Action:" in error_msg


def test_error_handling_bad_deadlines_format():
    """Test parsing error for invalid deadlines format.
    
    Requirements: 16.3
    """
    with pytest.raises(IssueParsingError) as exc_info:
        parse_issue_body(INVALID_ISSUE_BAD_DEADLINES)
    
    error_msg = str(exc_info.value)
    assert "ERROR: Invalid deadlines format" in error_msg
    assert "integer" in error_msg.lower()
    assert "Action:" in error_msg


def test_error_handling_bad_domains_format():
    """Test parsing error for invalid domains format.
    
    Requirements: 16.3
    """
    with pytest.raises(IssueParsingError) as exc_info:
        parse_issue_body(INVALID_ISSUE_BAD_DOMAINS)
    
    error_msg = str(exc_info.value)
    assert "ERROR: Invalid domains format" in error_msg
    assert "integer" in error_msg.lower()
    assert "Action:" in error_msg


def test_error_handling_empty_issue_body():
    """Test parsing error for empty Issue body.
    
    Requirements: 16.3
    """
    with pytest.raises(IssueParsingError) as exc_info:
        parse_issue_body("")
    
    error_msg = str(exc_info.value)
    assert "ERROR: Empty Issue body" in error_msg
    assert "Action:" in error_msg


def test_error_handling_whitespace_only_issue_body():
    """Test parsing error for whitespace-only Issue body.
    
    Requirements: 16.3
    """
    with pytest.raises(IssueParsingError) as exc_info:
        parse_issue_body("   \n\n   \t  ")
    
    error_msg = str(exc_info.value)
    assert "ERROR: Empty Issue body" in error_msg
    assert "Action:" in error_msg


def test_error_formatting_for_github():
    """Test that errors are properly formatted for GitHub comments.
    
    Requirements: 16.3
    """
    try:
        parse_issue_body(INVALID_ISSUE_MISSING_DEADLINES)
    except IssueParsingError as e:
        formatted = format_for_github(str(e))
        
        # Verify markdown code block
        assert formatted.startswith("```\n")
        assert formatted.endswith("\n```")
        
        # Verify error content is preserved
        assert "ERROR: Missing required field" in formatted
        assert "Action:" in formatted


def test_end_to_end_with_glue_script_normal():
    """Test complete glue script execution with NORMAL state.
    
    Requirements: 16.3, 20.5
    """
    result = subprocess.run(
        [sys.executable, "-m", "scripts.run_from_issue", VALID_ISSUE_NORMAL],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent  # Run from project root
    )
    
    # Verify success
    assert result.returncode == 0, f"Script failed with stderr: {result.stderr}"
    
    # Verify output format
    assert "```" in result.stdout
    assert "Personal Decision-Support System" in result.stdout
    assert "Current State: NORMAL" in result.stdout


def test_end_to_end_with_glue_script_overloaded():
    """Test complete glue script execution with OVERLOADED state.
    
    Requirements: 16.3, 20.5
    """
    result = subprocess.run(
        [sys.executable, "-m", "scripts.run_from_issue", VALID_ISSUE_OVERLOADED],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent  # Run from project root
    )
    
    # Verify success
    assert result.returncode == 0, f"Script failed with stderr: {result.stderr}"
    
    # Verify output format
    assert "```" in result.stdout
    assert "Current State: OVERLOADED" in result.stdout


def test_end_to_end_with_glue_script_parsing_error():
    """Test glue script error handling for parsing errors.
    
    Requirements: 16.3
    """
    result = subprocess.run(
        [sys.executable, "-m", "scripts.run_from_issue", INVALID_ISSUE_MISSING_DEADLINES],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent  # Run from project root
    )
    
    # Verify failure
    assert result.returncode == 1
    
    # Verify error in stderr
    assert "ERROR: Missing required field" in result.stderr
    assert "```" in result.stderr  # Formatted for GitHub


def test_end_to_end_with_glue_script_no_arguments():
    """Test glue script error handling when no arguments provided.
    
    Requirements: 16.3
    """
    result = subprocess.run(
        [sys.executable, "-m", "scripts.run_from_issue"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent  # Run from project root
    )
    
    # Verify failure
    assert result.returncode == 1
    
    # Verify error message
    assert "ERROR: Missing Issue body argument" in result.stderr
    assert "Usage:" in result.stderr
