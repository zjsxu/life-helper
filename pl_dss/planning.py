"""Planning Engine (L1) for Personal Life Orchestrator.

This module provides the interface for future planning functionality.
In this phase, it only checks Global Authority and returns appropriate
responses - no actual planning is implemented.

The Planning Engine:
- Checks Global Authority planning_permission before any operation
- Returns None + explanation when planning is DENIED
- Returns None + "not implemented" when planning is ALLOWED
- Does NOT implement scheduling, calendar modification, or optimization
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, List, Optional

from pl_dss.authority import GlobalAuthority


@dataclass
class Task:
    """Task with deadline and type.
    
    Attributes:
        name: Task name/description
        deadline: ISO format date (YYYY-MM-DD)
        type: Task type (e.g., "coursework", "admin", "work")
    """
    name: str
    deadline: str  # ISO format: YYYY-MM-DD
    type: str


@dataclass
class Constraint:
    """User-defined constraints on planning.
    
    Attributes:
        max_parallel_focus: Maximum tasks to focus on simultaneously
        no_work_after: Time boundary in HH:MM format (e.g., "22:00")
    """
    max_parallel_focus: Optional[int] = None
    no_work_after: Optional[str] = None  # HH:MM format


@dataclass
class AdvisoryOutput:
    """Descriptive, non-prescriptive planning suggestions.
    
    Attributes:
        observations: Descriptive observations about workload
        recommendations: High-level suggestions (not prescriptive)
        warnings: Risk flags and conflict warnings
    """
    observations: List[str]
    recommendations: List[str]
    warnings: List[str]


@dataclass
class PlanRequest:
    """Request for planning functionality.
    
    Attributes:
        tasks: List of tasks to plan
        constraints: Constraints on planning
        decision_state: Global Authority object from Decision Core
    """
    tasks: List[Task]
    constraints: Constraint
    decision_state: GlobalAuthority


@dataclass
class PlanResult:
    """Result from planning operation.
    
    Attributes:
        advisory: Advisory output (None when planning denied)
        reason: Explanation of the result
        blocked_by: What blocked planning (e.g., "Decision Core" when denied)
    """
    advisory: Optional[AdvisoryOutput]
    reason: str
    blocked_by: Optional[str]


def validate_task(task: Task) -> Optional[str]:
    """Validate task input structure and format.
    
    Checks:
    - Required fields are present (name, deadline, type)
    - Deadline format is valid ISO date (YYYY-MM-DD)
    
    Args:
        task: Task to validate
        
    Returns:
        None if valid, error message string if invalid
        
    Requirements: 13.2, 13.6, 13.7
    """
    # Check required fields
    if not task.name:
        return "Invalid task: missing name"
    
    if not task.deadline:
        return "Invalid task: missing deadline"
    
    if not task.type:
        return "Invalid task: missing type"
    
    # Validate deadline format (ISO date: YYYY-MM-DD)
    try:
        datetime.strptime(task.deadline, "%Y-%m-%d")
    except ValueError:
        return f"Invalid deadline format: expected YYYY-MM-DD, got '{task.deadline}'"
    
    return None


def analyze_deadline_clustering(tasks: List[Task]) -> List[str]:
    """Detect when multiple deadlines fall within tight windows.
    
    Detects when 3+ deadlines fall within a 3-day window.
    
    Args:
        tasks: List of tasks to analyze
        
    Returns:
        List of observations about deadline clustering
        
    Requirements: 15.1, 15.2, 15.3, 15.4
    """
    observations = []
    
    if len(tasks) < 3:
        return observations
    
    # Parse and sort deadlines
    deadline_dates = []
    for task in tasks:
        try:
            date = datetime.strptime(task.deadline, "%Y-%m-%d")
            deadline_dates.append(date)
        except ValueError:
            continue
    
    deadline_dates.sort()
    
    # Check for clustering (3+ deadlines within 3-day window)
    for i in range(len(deadline_dates) - 2):
        window_start = deadline_dates[i]
        # Count how many deadlines fall within 3 days of this one
        count = 1
        window_end = window_start
        
        for j in range(i + 1, len(deadline_dates)):
            days_diff = (deadline_dates[j] - window_start).days
            if days_diff <= 2:  # Within 3-day window (0, 1, 2 days apart)
                count += 1
                window_end = deadline_dates[j]
            else:
                break
        
        if count >= 3:
            # Format dates for output
            start_str = window_start.strftime("%b %d")
            end_str = window_end.strftime("%b %d")
            observations.append(
                f"{count} deadlines fall within a 3-day window ({start_str}-{end_str})"
            )
            break  # Only report the first cluster
    
    return observations


def assess_cognitive_load(tasks: List[Task], constraints: Constraint) -> List[str]:
    """Assess if workload exceeds safe thresholds.
    
    Compares task count to max_parallel_focus constraint.
    
    Args:
        tasks: List of tasks to assess
        constraints: User-defined constraints
        
    Returns:
        List of observations about cognitive load
        
    Requirements: 16.1, 16.2, 16.3
    """
    observations = []
    
    if constraints.max_parallel_focus is None:
        return observations
    
    task_count = len(tasks)
    
    # Check if task count exceeds max_parallel_focus
    if task_count > constraints.max_parallel_focus:
        observations.append("Cognitive load likely exceeds safe threshold")
        observations.append("This week exceeds your usual load")
    
    return observations


def suggest_prioritization(tasks: List[Task]) -> List[str]:
    """Provide high-level prioritization suggestions.
    
    Identifies task types and urgency to suggest focus areas.
    
    Args:
        tasks: List of tasks to analyze
        
    Returns:
        List of recommendations for prioritization
        
    Requirements: 17.1, 17.2, 17.3, 17.4
    """
    recommendations = []
    
    if not tasks:
        return recommendations
    
    # Count task types
    task_types = {}
    for task in tasks:
        task_type = task.type
        task_types[task_type] = task_types.get(task_type, 0) + 1
    
    # Identify primary task type
    if task_types:
        primary_type = max(task_types, key=task_types.get)
        
        # Suggest treating urgent tasks as primary focus
        if primary_type == "coursework":
            recommendations.append("Treat coursework as primary focus")
        elif primary_type == "work":
            recommendations.append("Treat work tasks as primary focus")
        
        # Suggest minimizing scope of lower-priority tasks
        if "admin" in task_types:
            recommendations.append("Minimize administrative scope")
        
        # Suggest avoiding optional tasks during high-load periods
        if len(tasks) > 2:
            recommendations.append("Avoid adding optional tasks this week")
    
    return recommendations


def detect_conflicts(tasks: List[Task], constraints: Constraint) -> List[str]:
    """Warn about potential conflicts and constraint violations.
    
    Detects:
    - Overlapping deadlines
    - Constraint violations
    
    Args:
        tasks: List of tasks to check
        constraints: User-defined constraints
        
    Returns:
        List of warnings about conflicts
        
    Requirements: 18.1, 18.2, 18.3, 18.4
    """
    warnings = []
    
    if not tasks:
        return warnings
    
    # Check for constraint violations (cognitive load)
    if constraints.max_parallel_focus is not None:
        if len(tasks) > constraints.max_parallel_focus:
            warnings.append("Task load exceeds max_parallel_focus constraint")
    
    # Check for overlapping deadlines (same deadline date)
    deadline_map = {}
    for task in tasks:
        deadline = task.deadline
        if deadline in deadline_map:
            deadline_map[deadline].append(task)
        else:
            deadline_map[deadline] = [task]
    
    # Find deadlines with multiple tasks
    for deadline, task_list in deadline_map.items():
        if len(task_list) > 1:
            warnings.append("Multiple high-priority tasks overlap")
            break  # Only report once
    
    return warnings


def format_advisory_output(advisory: AdvisoryOutput) -> str:
    """Format advisory output in structured plain text.
    
    Format:
    - Start with "PLANNING ADVISORY:"
    - Use bullet points (-) for observations
    - Use nested bullets (•) for recommendations
    - Plain text without formatting codes
    
    Args:
        advisory: AdvisoryOutput to format
        
    Returns:
        Formatted string
        
    Requirements: 19.1, 19.2, 19.3, 19.4, 19.5
    """
    lines = ["PLANNING ADVISORY:"]
    
    # Add observations with bullet points
    for obs in advisory.observations:
        lines.append(f"- {obs}")
    
    # Add warnings with bullet points
    for warning in advisory.warnings:
        lines.append(f"- {warning}")
    
    # Add recommendations with nested bullets
    if advisory.recommendations:
        lines.append("- Recommendation:")
        for rec in advisory.recommendations:
            lines.append(f"  • {rec}")
    
    return "\n".join(lines)


def propose_plan(request: PlanRequest) -> PlanResult:
    """Planning Advisor that provides high-level task analysis.
    
    When planning is ALLOWED:
    - Analyzes deadline clustering
    - Assesses cognitive load
    - Provides prioritization suggestions
    - Warns about conflicts
    - Returns descriptive, non-prescriptive advice
    
    When planning is DENIED:
    - Returns blocked message
    - Provides no analysis or suggestions
    
    NEVER:
    - Schedules specific times
    - Modifies calendars
    - Executes actions
    - Uses optimization language
    
    Args:
        request: PlanRequest with tasks, constraints, and authority
        
    Returns:
        PlanResult with advisory output or blocked message
        
    Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 15.5, 16.4, 16.5, 
                  18.5, 20.1, 20.2, 20.3, 20.4, 20.5, 20.6, 20.7
    """
    # Check Global Authority planning permission (Requirement 14.1)
    if request.decision_state.planning == "DENIED":
        # Planning is denied - return blocked message (Requirements 14.2, 14.3, 14.4)
        return PlanResult(
            advisory=None,
            reason="ADVICE BLOCKED\nReason: Planning forbidden by Decision Core",
            blocked_by="Decision Core"
        )
    
    # Planning is allowed - perform advisory analysis
    # Validate task inputs
    for task in request.tasks:
        error = validate_task(task)
        if error:
            return PlanResult(
                advisory=None,
                reason=error,
                blocked_by=None
            )
    
    # Ensure input immutability - work with copies (Requirement 18.5)
    # Note: dataclasses are passed by reference, but we don't modify them
    
    # Perform analysis
    observations = []
    recommendations = []
    warnings = []
    
    # Analyze deadline clustering (Requirements 15.1, 15.2, 15.3, 15.4)
    clustering_obs = analyze_deadline_clustering(request.tasks)
    observations.extend(clustering_obs)
    
    # Assess cognitive load (Requirements 16.1, 16.2, 16.3)
    load_obs = assess_cognitive_load(request.tasks, request.constraints)
    observations.extend(load_obs)
    
    # Detect conflicts (Requirements 18.1, 18.2, 18.3, 18.4)
    conflict_warnings = detect_conflicts(request.tasks, request.constraints)
    warnings.extend(conflict_warnings)
    
    # Suggest prioritization (Requirements 17.1, 17.2, 17.3, 17.4)
    priority_recs = suggest_prioritization(request.tasks)
    recommendations.extend(priority_recs)
    
    # Create advisory output (descriptive, non-prescriptive)
    # Requirements: 15.5, 16.4, 16.5, 20.1, 20.4, 20.5, 20.6, 20.7
    advisory = AdvisoryOutput(
        observations=observations,
        recommendations=recommendations,
        warnings=warnings
    )
    
    return PlanResult(
        advisory=advisory,
        reason="Advisory analysis complete",
        blocked_by=None
    )
