"""Emergency rule engine for PL-DSS."""

from dataclasses import dataclass
from typing import List

from pl_dss.config import Config


@dataclass
class RuleResult:
    """Result from rule engine containing active rules and state."""
    active_rules: List[str]
    state: str


def get_active_rules(state: str, config: Config) -> RuleResult:
    """Return applicable downgrade rules for the given state.
    
    Simple lookup from config.downgrade_rules[state].
    Returns empty list for NORMAL state.
    
    Args:
        state: Current system state ("NORMAL", "STRESSED", or "OVERLOADED")
        config: System configuration containing downgrade rules
        
    Returns:
        RuleResult containing list of active rules and the state
        
    Requirements: 2.1, 2.2, 2.3, 2.5
    """
    # NORMAL state has no downgrade rules
    if state == "NORMAL":
        return RuleResult(active_rules=[], state=state)
    
    # For STRESSED or OVERLOADED, return configured rules without modification
    rules = config.downgrade_rules.get(state, [])
    
    return RuleResult(active_rules=rules, state=state)
