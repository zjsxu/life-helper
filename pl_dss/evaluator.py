"""State evaluation module for PL-DSS."""

from dataclasses import dataclass
from typing import List


@dataclass
class StateInputs:
    """Input data for state evaluation."""
    fixed_deadlines_14d: int
    active_high_load_domains: int
    energy_scores_last_3_days: List[int]


@dataclass
class StateResult:
    """Result of state evaluation."""
    state: str  # "NORMAL" | "STRESSED" | "OVERLOADED"
    explanation: str
    conditions_met: List[str]


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


def validate_energy_scores(energy_scores: List[int]) -> None:
    """Validate energy scores input.
    
    Args:
        energy_scores: List of daily energy ratings
        
    Raises:
        ValidationError: If energy scores are invalid
    """
    if not isinstance(energy_scores, list):
        raise ValidationError(
            "ERROR: Invalid energy scores format\n"
            "Details: Energy scores must be a list\n"
            "Expected: List of 3 integers between 1 and 5"
        )
    
    if len(energy_scores) != 3:
        raise ValidationError(
            "ERROR: Invalid energy scores count\n"
            f"Details: Received {len(energy_scores)} values\n"
            "Expected: Energy scores must be 3 integers between 1 and 5"
        )
    
    for i, score in enumerate(energy_scores):
        if not isinstance(score, int):
            raise ValidationError(
                "ERROR: Invalid energy score type\n"
                f"Details: Score at position {i} is {type(score).__name__}, not int\n"
                "Expected: Energy scores must be 3 integers between 1 and 5"
            )
        
        if score < 1 or score > 5:
            raise ValidationError(
                "ERROR: Energy score out of range\n"
                f"Details: Score at position {i} is {score}\n"
                "Expected: Energy scores must be 3 integers between 1 and 5"
            )


def validate_fixed_deadlines(fixed_deadlines_14d: int) -> None:
    """Validate fixed deadlines input.
    
    Args:
        fixed_deadlines_14d: Number of fixed deadlines in next 14 days
        
    Raises:
        ValidationError: If fixed deadlines value is invalid
    """
    if not isinstance(fixed_deadlines_14d, int):
        raise ValidationError(
            "ERROR: Invalid fixed deadlines type\n"
            f"Details: Received {type(fixed_deadlines_14d).__name__}\n"
            "Expected: Fixed deadlines must be a non-negative integer"
        )
    
    if fixed_deadlines_14d < 0:
        raise ValidationError(
            "ERROR: Invalid fixed deadlines value\n"
            f"Details: Received {fixed_deadlines_14d}\n"
            "Expected: Fixed deadlines must be a non-negative integer"
        )


def validate_active_high_load_domains(active_high_load_domains: int) -> None:
    """Validate active high-load domains input.
    
    Args:
        active_high_load_domains: Number of active high-load domains
        
    Raises:
        ValidationError: If active high-load domains value is invalid
    """
    if not isinstance(active_high_load_domains, int):
        raise ValidationError(
            "ERROR: Invalid active high-load domains type\n"
            f"Details: Received {type(active_high_load_domains).__name__}\n"
            "Expected: Active high-load domains must be a non-negative integer"
        )
    
    if active_high_load_domains < 0:
        raise ValidationError(
            "ERROR: Invalid active high-load domains value\n"
            f"Details: Received {active_high_load_domains}\n"
            "Expected: Active high-load domains must be a non-negative integer"
        )


def validate_inputs(inputs: StateInputs) -> None:
    """Validate all inputs.
    
    Args:
        inputs: StateInputs object to validate
        
    Raises:
        ValidationError: If any input is invalid
    """
    validate_energy_scores(inputs.energy_scores_last_3_days)
    validate_fixed_deadlines(inputs.fixed_deadlines_14d)
    validate_active_high_load_domains(inputs.active_high_load_domains)


def compute_average_energy(energy_scores: List[int]) -> float:
    """Compute average of energy scores.
    
    Args:
        energy_scores: List of 3 energy scores
        
    Returns:
        Average energy score as float
    """
    return sum(energy_scores) / len(energy_scores)


def count_conditions_met(inputs: StateInputs, config) -> tuple[int, List[str]]:
    """Count how many overload conditions are met.
    
    Args:
        inputs: Validated state inputs
        config: System configuration with thresholds
        
    Returns:
        Tuple of (count, list of condition descriptions)
    """
    conditions_met = []
    thresholds = config.thresholds.overload
    
    # Check fixed deadlines condition
    if inputs.fixed_deadlines_14d >= thresholds.fixed_deadlines_14d:
        conditions_met.append(
            f"Fixed deadlines ({inputs.fixed_deadlines_14d}) >= threshold ({thresholds.fixed_deadlines_14d})"
        )
    
    # Check active high-load domains condition
    if inputs.active_high_load_domains >= thresholds.active_high_load_domains:
        conditions_met.append(
            f"High-load domains ({inputs.active_high_load_domains}) >= threshold ({thresholds.active_high_load_domains})"
        )
    
    # Check average energy condition
    avg_energy = compute_average_energy(inputs.energy_scores_last_3_days)
    if avg_energy <= thresholds.avg_energy_score:
        conditions_met.append(
            f"Average energy ({avg_energy:.1f}) <= threshold ({thresholds.avg_energy_score})"
        )
    
    return len(conditions_met), conditions_met


def determine_state(conditions_count: int) -> str:
    """Determine system state based on number of conditions met.
    
    Args:
        conditions_count: Number of overload conditions that are true
        
    Returns:
        System state: "NORMAL", "STRESSED", or "OVERLOADED"
    """
    if conditions_count >= 2:
        return "OVERLOADED"
    elif conditions_count == 1:
        return "STRESSED"
    else:
        return "NORMAL"


def generate_explanation(state: str, conditions_count: int, conditions_met: List[str]) -> str:
    """Generate explanation for the determined state.
    
    Args:
        state: Determined system state
        conditions_count: Number of conditions met
        conditions_met: List of condition descriptions
        
    Returns:
        Human-readable explanation string
    """
    if conditions_count == 0:
        return "No overload conditions met"
    elif conditions_count == 1:
        return f"1 condition met:\n  • {conditions_met[0]}"
    else:
        conditions_str = "\n  • ".join(conditions_met)
        return f"{conditions_count} conditions met:\n  • {conditions_str}"


def evaluate_state(inputs: StateInputs, config) -> StateResult:
    """Evaluate system state based on inputs and configured thresholds.
    
    Args:
        inputs: StateInputs with user-provided data
        config: System configuration with thresholds
        
    Returns:
        StateResult with state, explanation, and conditions met
        
    Raises:
        ValidationError: If inputs are invalid
    """
    # Validate inputs
    validate_inputs(inputs)
    
    # Count conditions met
    conditions_count, conditions_met = count_conditions_met(inputs, config)
    
    # Determine state
    state = determine_state(conditions_count)
    
    # Generate explanation
    explanation = generate_explanation(state, conditions_count, conditions_met)
    
    return StateResult(
        state=state,
        explanation=explanation,
        conditions_met=conditions_met
    )
