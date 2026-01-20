"""Global Authority module for Personal Life Orchestrator.

This module derives authority from Decision Core output and controls
all downstream operations (Planning Engine and Execution Layer).

All authority flows from L0 (Decision Core) through this module to
L1 (Planning Engine) and L2 (Execution Layer).
"""

from dataclasses import dataclass
from typing import List

from pl_dss.evaluator import StateResult
from pl_dss.rules import RuleResult


@dataclass
class GlobalAuthority:
    """Global Authority object that controls all downstream operations.
    
    Attributes:
        planning: Planning permission ("ALLOWED" or "DENIED")
        execution: Execution permission ("ALLOWED" or "DENIED")
        mode: Authority mode ("NORMAL", "CONTAINMENT", or "RECOVERY")
        state: System state from Decision Core ("NORMAL", "STRESSED", or "OVERLOADED")
        active_rules: List of active downgrade rules from Decision Core
    """
    planning: str
    execution: str
    mode: str
    state: str
    active_rules: List[str]


def derive_authority(state_result: StateResult, rule_result: RuleResult) -> GlobalAuthority:
    """Derive Global Authority from Decision Core output.
    
    Authority Derivation Rules:
    - OVERLOADED → planning: DENIED, mode: CONTAINMENT
    - STRESSED → planning: DENIED, mode: CONTAINMENT
    - NORMAL → planning: ALLOWED, mode: NORMAL
    - execution: ALWAYS DENIED in this version
    
    Args:
        state_result: Output from Decision Core state evaluation
        rule_result: Output from Decision Core rule engine
        
    Returns:
        GlobalAuthority object with all permissions and mode
        
    Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8
    """
    state = state_result.state
    active_rules = rule_result.active_rules
    
    # Derive planning permission and mode based on state
    if state == "OVERLOADED":
        planning = "DENIED"
        mode = "CONTAINMENT"
    elif state == "STRESSED":
        planning = "DENIED"
        mode = "CONTAINMENT"
    elif state == "NORMAL":
        planning = "ALLOWED"
        mode = "NORMAL"
    else:
        # Defensive: should never happen with valid Decision Core output
        planning = "DENIED"
        mode = "CONTAINMENT"
    
    # Execution is always denied in this system version
    execution = "DENIED"
    
    return GlobalAuthority(
        planning=planning,
        execution=execution,
        mode=mode,
        state=state,
        active_rules=active_rules
    )
