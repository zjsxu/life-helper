"""Unit tests for Execution Layer (L2).

Tests that the Execution Layer module exists, raises ExecutionError on any
execution attempt, and provides the correct error message.

Requirements: 3.1
"""

import pytest
from hypothesis import given, strategies as st, settings
from pl_dss.execution import execute_action, ExecutionError
from pl_dss.authority import GlobalAuthority


def test_execution_module_exists():
    """Test that the execution module exists and can be imported.
    
    Validates that the execution layer module is present in the system
    and provides the required interface.
    
    Requirements: 3.1
    """
    # If we can import these, the module exists
    from pl_dss import execution
    
    # Verify the module has the required components
    assert hasattr(execution, 'execute_action')
    assert hasattr(execution, 'ExecutionError')
    assert callable(execution.execute_action)
    assert issubclass(execution.ExecutionError, Exception)


def test_execution_error_is_raised():
    """Test that ExecutionError is raised when execution is attempted.
    
    Validates that any attempt to execute an action results in ExecutionError,
    regardless of the action or authority provided.
    
    Requirements: 3.1
    """
    # Create a sample authority object (doesn't matter what it contains)
    authority = GlobalAuthority(
        planning="ALLOWED",
        execution="DENIED",
        mode="NORMAL",
        state="NORMAL",
        active_rules=[]
    )
    
    # Attempt execution with any action
    with pytest.raises(ExecutionError):
        execute_action(action="test_action", authority=authority)
    
    # Try with different action types
    with pytest.raises(ExecutionError):
        execute_action(action={"type": "calendar_event"}, authority=authority)
    
    with pytest.raises(ExecutionError):
        execute_action(action=None, authority=authority)
    
    # Try with different authority states
    authority_denied = GlobalAuthority(
        planning="DENIED",
        execution="DENIED",
        mode="CONTAINMENT",
        state="OVERLOADED",
        active_rules=["No new commitments"]
    )
    
    with pytest.raises(ExecutionError):
        execute_action(action="test_action", authority=authority_denied)


def test_execution_error_message_is_correct():
    """Test that ExecutionError contains the correct error message.
    
    Validates that the error message clearly states that automation is
    disabled in the current system version.
    
    Requirements: 3.1
    """
    # Create a sample authority object
    authority = GlobalAuthority(
        planning="ALLOWED",
        execution="DENIED",
        mode="NORMAL",
        state="NORMAL",
        active_rules=[]
    )
    
    # Capture the exception and verify the message
    with pytest.raises(ExecutionError) as exc_info:
        execute_action(action="test_action", authority=authority)
    
    # Verify the exact error message
    assert str(exc_info.value) == "Automation disabled in current system version"
    
    # Verify the error message is consistent across different calls
    with pytest.raises(ExecutionError) as exc_info2:
        execute_action(action="different_action", authority=authority)
    
    assert str(exc_info2.value) == "Automation disabled in current system version"


def test_execution_error_is_exception_subclass():
    """Test that ExecutionError is a proper Exception subclass.
    
    Validates that ExecutionError can be caught as a standard exception
    and follows Python exception conventions.
    
    Requirements: 3.1
    """
    # Verify ExecutionError is an Exception subclass
    assert issubclass(ExecutionError, Exception)
    
    # Verify it can be caught as a general Exception
    authority = GlobalAuthority(
        planning="ALLOWED",
        execution="DENIED",
        mode="NORMAL",
        state="NORMAL",
        active_rules=[]
    )
    
    try:
        execute_action(action="test", authority=authority)
        assert False, "Should have raised ExecutionError"
    except Exception as e:
        # Should be catchable as Exception
        assert isinstance(e, ExecutionError)
        assert str(e) == "Automation disabled in current system version"



# Property-Based Tests

@settings(max_examples=100)
@given(
    action=st.one_of(
        st.none(),
        st.text(),
        st.integers(),
        st.lists(st.text()),
        st.dictionaries(st.text(), st.text()),
    ),
    planning=st.sampled_from(["ALLOWED", "DENIED"]),
    execution=st.sampled_from(["ALLOWED", "DENIED"]),
    mode=st.sampled_from(["NORMAL", "CONTAINMENT", "RECOVERY"]),
    state=st.sampled_from(["NORMAL", "STRESSED", "OVERLOADED"]),
    active_rules=st.lists(st.text(), max_size=5)
)
def test_property_execution_prohibition(action, planning, execution, mode, state, active_rules):
    """Property test: Execution Layer always raises ExecutionError.
    
    Feature: github-interface, Property 15: Execution Layer Prohibition
    
    For any execution attempt, the Execution Layer should raise ExecutionError
    with a clear message explaining that automation is disabled.
    
    This property validates that:
    1. ExecutionError is raised for ANY action input (None, string, dict, list, etc.)
    2. ExecutionError is raised regardless of authority state
    3. The error message is consistent and clear
    4. No execution ever succeeds
    
    Validates: Requirements 9.1, 9.2, 9.4
    """
    # Create authority with random valid values
    authority = GlobalAuthority(
        planning=planning,
        execution=execution,
        mode=mode,
        state=state,
        active_rules=active_rules
    )
    
    # Execution should ALWAYS raise ExecutionError, regardless of inputs
    with pytest.raises(ExecutionError) as exc_info:
        execute_action(action=action, authority=authority)
    
    # Verify the error message is correct
    assert str(exc_info.value) == "Automation disabled in current system version"



# Documentation Tests

def test_execution_module_has_prohibition_documentation():
    """Test that execution.py contains clear prohibition documentation.
    
    Validates that the execution module includes comprehensive documentation
    explaining why execution is disabled and what the safety boundaries are.
    
    Requirements: 9.3, 9.5
    """
    import os
    
    # Read the execution.py file
    execution_file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'pl_dss',
        'execution.py'
    )
    
    with open(execution_file_path, 'r') as f:
        content = f.read()
    
    # Verify key documentation elements are present
    assert "Explicitly Disabled" in content or "explicitly FORBIDDEN" in content, \
        "Module should document that execution is explicitly disabled"
    
    assert "ExecutionError" in content, \
        "Module should document ExecutionError"
    
    assert "safety" in content.lower() or "Safety" in content, \
        "Module should mention safety considerations"
    
    assert "disabled" in content.lower(), \
        "Module should explicitly state execution is disabled"
    
    # Verify the execute_action function has documentation
    assert "def execute_action" in content, \
        "Module should define execute_action function"
    
    assert "Automation disabled" in content, \
        "Module should contain the error message about automation being disabled"


def test_readme_documents_execution_disabled():
    """Test that README documents that execution is disabled.
    
    Validates that the README includes information about the execution
    layer being disabled in the current system version.
    
    Requirements: 9.3, 9.5
    """
    import os
    
    # Read the README.md file
    readme_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'README.md'
    )
    
    with open(readme_path, 'r') as f:
        content = f.read()
    
    # Verify execution is documented as disabled
    # Check for System Constitution section which should mention execution
    assert "System Constitution" in content, \
        "README should contain System Constitution section"
    
    assert "Execution is disabled by design" in content, \
        "README should explicitly state execution is disabled by design"
    
    # Verify the constitution mentions automation boundaries
    assert "automation" in content.lower() or "Automation" in content, \
        "README should mention automation in context of execution"
