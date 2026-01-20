"""Recovery monitoring module for PL-DSS."""

from dataclasses import dataclass
from typing import List


@dataclass
class RecoveryResult:
    """Result of recovery evaluation."""
    can_recover: bool
    explanation: str
    blocking_conditions: List[str]


def check_recovery(inputs, current_state, config) -> RecoveryResult:
    """Determine if recovery to NORMAL is possible.
    
    Recovery conditions (all must be true):
    - fixed_deadlines_14d <= recovery threshold
    - active_high_load_domains <= recovery threshold
    - avg(energy_scores) >= recovery threshold
    
    Args:
        inputs: StateInputs with current user data
        current_state: Current system state
        config: System configuration with recovery thresholds
        
    Returns:
        RecoveryResult with recovery status, explanation, and blocking conditions
    """
    recovery_thresholds = config.thresholds.recovery
    blocking_conditions = []
    
    # Check fixed deadlines condition
    if inputs.fixed_deadlines_14d > recovery_thresholds.fixed_deadlines_14d:
        blocking_conditions.append(
            f"Fixed deadlines ({inputs.fixed_deadlines_14d}) > recovery threshold ({recovery_thresholds.fixed_deadlines_14d})"
        )
    
    # Check active high-load domains condition
    if inputs.active_high_load_domains > recovery_thresholds.active_high_load_domains:
        blocking_conditions.append(
            f"High-load domains ({inputs.active_high_load_domains}) > recovery threshold ({recovery_thresholds.active_high_load_domains})"
        )
    
    # Check average energy condition
    avg_energy = sum(inputs.energy_scores_last_3_days) / len(inputs.energy_scores_last_3_days)
    if avg_energy < recovery_thresholds.avg_energy_score:
        blocking_conditions.append(
            f"Average energy ({avg_energy:.1f}) < recovery threshold ({recovery_thresholds.avg_energy_score})"
        )
    
    # Determine if recovery is possible
    can_recover = len(blocking_conditions) == 0
    
    # Generate explanation
    if can_recover:
        explanation = "All recovery conditions met. Safe to return to NORMAL mode."
        if config.recovery_advice:
            advice_str = "\n  • ".join(config.recovery_advice)
            explanation += f"\n  • {advice_str}"
    else:
        explanation = "Recovery not ready. Blocking conditions:"
        blocking_str = "\n  • ".join(blocking_conditions)
        explanation += f"\n  • {blocking_str}"
    
    return RecoveryResult(
        can_recover=can_recover,
        explanation=explanation,
        blocking_conditions=blocking_conditions
    )
