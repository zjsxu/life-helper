"""Unit tests for Execution Layer (L2).

Tests that the Execution Layer module exists, raises ExecutionError on any
execution attempt, and provides the correct error message.

Requirements: 3.1
"""

import pytest
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
