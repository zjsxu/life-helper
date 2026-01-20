"""Unit tests for Planning Engine interface.

Tests the basic Planning Engine interface functionality:
- Function exists with correct signature
- Behavior with DENIED authority
- Behavior with ALLOWED authority

Requirements: 2.1
"""

import pytest

from pl_dss.planning import (
    PlanRequest,
    PlanResult,
    propose_plan,
    Task,
    Constraint,
    AdvisoryOutput
)
from pl_dss.authority import GlobalAuthority


@pytest.fixture
def denied_authority():
    """Create a GlobalAuthority with planning DENIED."""
    return GlobalAuthority(
        planning="DENIED",
        execution="DENIED",
        mode="CONTAINMENT",
        state="OVERLOADED",
        active_rules=["No new commitments", "Pause technical tool development"]
    )


@pytest.fixture
def allowed_authority():
    """Create a GlobalAuthority with planning ALLOWED."""
    return GlobalAuthority(
        planning="ALLOWED",
        execution="DENIED",
        mode="NORMAL",
        state="NORMAL",
        active_rules=[]
    )


def test_propose_plan_function_exists():
    """Test that propose_plan function exists with correct signature.
    
    Validates that:
    - Function exists and is callable
    - Function accepts PlanRequest parameter
    - Function returns PlanResult
    
    Requirements: 2.1
    """
    # Verify function exists
    assert callable(propose_plan)
    
    # Verify function signature by calling it with minimal valid input
    authority = GlobalAuthority(
        planning="DENIED",
        execution="DENIED",
        mode="CONTAINMENT",
        state="OVERLOADED",
        active_rules=[]
    )
    
    request = PlanRequest(
        tasks=[],
        constraints=Constraint(),
        decision_state=authority
    )
    
    result = propose_plan(request)
    
    # Verify return type is PlanResult
    assert isinstance(result, PlanResult)
    assert hasattr(result, 'advisory')
    assert hasattr(result, 'reason')
    assert hasattr(result, 'blocked_by')


def test_propose_plan_with_denied_authority(denied_authority):
    """Test propose_plan with DENIED authority.
    
    Validates that when planning permission is DENIED:
    - Returns PlanResult with advisory=None
    - Returns reason containing "ADVICE BLOCKED"
    - Returns reason containing "Planning forbidden by Decision Core"
    - Returns blocked_by="Decision Core"
    - Does NOT provide any advisory analysis
    
    Requirements: 2.1, 2.3, 2.4
    """
    # Create request with DENIED authority
    request = PlanRequest(
        tasks=[
            Task(name="Test Task", deadline="2026-02-15", type="work")
        ],
        constraints=Constraint(max_parallel_focus=2),
        decision_state=denied_authority
    )
    
    # Call propose_plan
    result = propose_plan(request)
    
    # Verify planning was blocked
    assert result.advisory is None
    assert "ADVICE BLOCKED" in result.reason
    assert "Planning forbidden by Decision Core" in result.reason
    assert result.blocked_by == "Decision Core"


def test_propose_plan_with_allowed_authority(allowed_authority):
    """Test propose_plan with ALLOWED authority.
    
    Validates that when planning permission is ALLOWED:
    - Returns PlanResult with advisory (not None)
    - Advisory is an AdvisoryOutput object
    - Returns appropriate reason
    - blocked_by is None
    - Provides advisory analysis
    
    Requirements: 2.1, 2.5
    """
    # Create request with ALLOWED authority
    request = PlanRequest(
        tasks=[
            Task(name="Test Task 1", deadline="2026-02-15", type="coursework"),
            Task(name="Test Task 2", deadline="2026-02-16", type="admin")
        ],
        constraints=Constraint(max_parallel_focus=2),
        decision_state=allowed_authority
    )
    
    # Call propose_plan
    result = propose_plan(request)
    
    # Verify planning was not blocked
    assert result.advisory is not None
    assert isinstance(result.advisory, AdvisoryOutput)
    assert result.reason == "Advisory analysis complete"
    assert result.blocked_by is None
    
    # Verify advisory has expected structure
    assert hasattr(result.advisory, 'observations')
    assert hasattr(result.advisory, 'recommendations')
    assert hasattr(result.advisory, 'warnings')
    assert isinstance(result.advisory.observations, list)
    assert isinstance(result.advisory.recommendations, list)
    assert isinstance(result.advisory.warnings, list)


def test_propose_plan_with_allowed_authority_empty_tasks(allowed_authority):
    """Test propose_plan with ALLOWED authority and empty task list.
    
    Validates that the function handles empty task lists gracefully
    when planning is allowed.
    
    Requirements: 2.1
    """
    # Create request with empty tasks
    request = PlanRequest(
        tasks=[],
        constraints=Constraint(),
        decision_state=allowed_authority
    )
    
    # Call propose_plan
    result = propose_plan(request)
    
    # Verify planning was not blocked
    assert result.advisory is not None
    assert isinstance(result.advisory, AdvisoryOutput)
    assert result.reason == "Advisory analysis complete"
    assert result.blocked_by is None


def test_propose_plan_respects_authority_state(denied_authority, allowed_authority):
    """Test that propose_plan respects the authority state consistently.
    
    Validates that the same request produces different results based on
    the authority state.
    
    Requirements: 2.1, 2.2
    """
    # Create identical task lists
    tasks = [
        Task(name="Task 1", deadline="2026-02-15", type="work"),
        Task(name="Task 2", deadline="2026-02-16", type="work")
    ]
    constraints = Constraint(max_parallel_focus=2)
    
    # Request with DENIED authority
    request_denied = PlanRequest(
        tasks=tasks,
        constraints=constraints,
        decision_state=denied_authority
    )
    result_denied = propose_plan(request_denied)
    
    # Request with ALLOWED authority
    request_allowed = PlanRequest(
        tasks=tasks,
        constraints=constraints,
        decision_state=allowed_authority
    )
    result_allowed = propose_plan(request_allowed)
    
    # Verify different results based on authority
    assert result_denied.advisory is None
    assert result_allowed.advisory is not None
    
    assert "ADVICE BLOCKED" in result_denied.reason
    assert "Advisory analysis complete" == result_allowed.reason
    
    assert result_denied.blocked_by == "Decision Core"
    assert result_allowed.blocked_by is None


# Unit tests for Planning Advisor (Task 2.19)
# Requirements: 13.4, 13.5, 20.3


def test_constraint_max_parallel_focus_support(allowed_authority):
    """Test that Planning Advisor supports max_parallel_focus constraint.
    
    Validates that:
    - max_parallel_focus constraint is accepted
    - Cognitive load assessment uses the constraint
    - Warnings are generated when constraint is exceeded
    
    Requirements: 13.4
    """
    # Create request with max_parallel_focus constraint
    tasks = [
        Task(name="Task 1", deadline="2026-02-15", type="work"),
        Task(name="Task 2", deadline="2026-02-16", type="work"),
        Task(name="Task 3", deadline="2026-02-17", type="work"),
    ]
    
    request = PlanRequest(
        tasks=tasks,
        constraints=Constraint(max_parallel_focus=2),
        decision_state=allowed_authority
    )
    
    # Call propose_plan
    result = propose_plan(request)
    
    # Verify constraint was processed
    assert result.advisory is not None
    
    # Verify cognitive load assessment detected constraint violation
    # (3 tasks > max_parallel_focus of 2)
    assert len(result.advisory.observations) > 0
    assert any("Cognitive load" in obs for obs in result.advisory.observations)
    
    # Verify warning about constraint violation
    assert len(result.advisory.warnings) > 0
    assert any("max_parallel_focus" in warning for warning in result.advisory.warnings)


def test_constraint_time_boundary_support(allowed_authority):
    """Test that Planning Advisor supports time boundary constraints.
    
    Validates that:
    - no_work_after constraint is accepted
    - Constraint is stored in the request
    - System doesn't crash with time boundary constraint
    
    Requirements: 13.5
    """
    # Create request with no_work_after constraint
    tasks = [
        Task(name="Task 1", deadline="2026-02-15", type="work"),
    ]
    
    request = PlanRequest(
        tasks=tasks,
        constraints=Constraint(no_work_after="22:00"),
        decision_state=allowed_authority
    )
    
    # Call propose_plan
    result = propose_plan(request)
    
    # Verify constraint was accepted (no error)
    assert result.advisory is not None
    assert result.reason == "Advisory analysis complete"
    
    # Verify the constraint is properly stored
    assert request.constraints.no_work_after == "22:00"


def test_constraint_both_constraints_support(allowed_authority):
    """Test that Planning Advisor supports both constraints simultaneously.
    
    Validates that:
    - Both max_parallel_focus and no_work_after can be used together
    - System processes both constraints without error
    
    Requirements: 13.4, 13.5
    """
    # Create request with both constraints
    tasks = [
        Task(name="Task 1", deadline="2026-02-15", type="work"),
        Task(name="Task 2", deadline="2026-02-16", type="work"),
    ]
    
    request = PlanRequest(
        tasks=tasks,
        constraints=Constraint(
            max_parallel_focus=3,
            no_work_after="22:00"
        ),
        decision_state=allowed_authority
    )
    
    # Call propose_plan
    result = propose_plan(request)
    
    # Verify both constraints were accepted
    assert result.advisory is not None
    assert result.reason == "Advisory analysis complete"
    assert request.constraints.max_parallel_focus == 3
    assert request.constraints.no_work_after == "22:00"


def test_planning_advisor_does_not_call_execution_layer(allowed_authority):
    """Test that Planning Advisor doesn't call execution layer functions.
    
    Validates that:
    - Planning Advisor completes without calling execute_action
    - No ExecutionError is raised during planning
    - Planning remains purely advisory (no automation)
    
    This test verifies architectural separation between L1 (Planning) and
    L2 (Execution) layers.
    
    Requirements: 20.3
    """
    # Import execution module to verify it's not called
    from pl_dss import execution
    
    # Track if execute_action was called
    original_execute = execution.execute_action
    call_count = [0]
    
    def mock_execute(*args, **kwargs):
        call_count[0] += 1
        return original_execute(*args, **kwargs)
    
    # Temporarily replace execute_action to track calls
    execution.execute_action = mock_execute
    
    try:
        # Create request with tasks
        tasks = [
            Task(name="Task 1", deadline="2026-02-15", type="work"),
            Task(name="Task 2", deadline="2026-02-16", type="admin"),
            Task(name="Task 3", deadline="2026-02-17", type="coursework"),
        ]
        
        request = PlanRequest(
            tasks=tasks,
            constraints=Constraint(max_parallel_focus=2),
            decision_state=allowed_authority
        )
        
        # Call propose_plan
        result = propose_plan(request)
        
        # Verify planning completed successfully
        assert result.advisory is not None
        assert result.reason == "Advisory analysis complete"
        
        # Verify execute_action was NEVER called
        assert call_count[0] == 0, "Planning Advisor should not call execution layer"
        
    finally:
        # Restore original function
        execution.execute_action = original_execute


def test_planning_advisor_no_execution_with_denied_authority(denied_authority):
    """Test that Planning Advisor doesn't call execution even when denied.
    
    Validates that:
    - Even when planning is denied, no execution is attempted
    - System remains purely advisory
    
    Requirements: 20.3
    """
    # Import execution module
    from pl_dss import execution
    
    # Track if execute_action was called
    original_execute = execution.execute_action
    call_count = [0]
    
    def mock_execute(*args, **kwargs):
        call_count[0] += 1
        return original_execute(*args, **kwargs)
    
    execution.execute_action = mock_execute
    
    try:
        # Create request with DENIED authority
        tasks = [
            Task(name="Task 1", deadline="2026-02-15", type="work"),
        ]
        
        request = PlanRequest(
            tasks=tasks,
            constraints=Constraint(max_parallel_focus=2),
            decision_state=denied_authority
        )
        
        # Call propose_plan
        result = propose_plan(request)
        
        # Verify planning was blocked
        assert result.advisory is None
        assert "ADVICE BLOCKED" in result.reason
        
        # Verify execute_action was NEVER called
        assert call_count[0] == 0, "Planning Advisor should not call execution layer"
        
    finally:
        # Restore original function
        execution.execute_action = original_execute
