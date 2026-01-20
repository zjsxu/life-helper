#!/usr/bin/env python3
"""
Manual test script for GUI functionality
This script tests the GUI components without actually launching the window
"""

from pl_dss.gui import PLDSS_GUI
from pl_dss.config import load_config
from pl_dss.evaluator import StateInputs, evaluate_state
from pl_dss.rules import get_active_rules
from pl_dss.recovery import check_recovery

def test_gui_backend():
    """Test that GUI backend logic works correctly"""
    print("Testing GUI backend logic...")
    
    # Load config
    config = load_config()
    print("✓ Configuration loaded")
    
    # Test case 1: OVERLOADED state
    inputs = StateInputs(
        fixed_deadlines_14d=4,
        active_high_load_domains=3,
        energy_scores_last_3_days=[2, 3, 2]
    )
    
    state_result = evaluate_state(inputs, config)
    assert state_result.state == "OVERLOADED", "Expected OVERLOADED state"
    print(f"✓ State evaluation: {state_result.state}")
    
    rules_result = get_active_rules(state_result.state, config)
    assert len(rules_result.active_rules) > 0, "Expected active rules"
    print(f"✓ Rules retrieved: {len(rules_result.active_rules)} rules")
    
    recovery_result = check_recovery(inputs, state_result.state, config)
    assert not recovery_result.can_recover, "Should not be able to recover"
    print(f"✓ Recovery check: {recovery_result.can_recover}")
    
    # Test case 2: NORMAL state
    inputs = StateInputs(
        fixed_deadlines_14d=1,
        active_high_load_domains=1,
        energy_scores_last_3_days=[4, 5, 4]
    )
    
    state_result = evaluate_state(inputs, config)
    assert state_result.state == "NORMAL", "Expected NORMAL state"
    print(f"✓ State evaluation: {state_result.state}")
    
    rules_result = get_active_rules(state_result.state, config)
    assert len(rules_result.active_rules) == 0, "Expected no active rules"
    print(f"✓ Rules retrieved: {len(rules_result.active_rules)} rules")
    
    recovery_result = check_recovery(inputs, state_result.state, config)
    assert recovery_result.can_recover, "Should be able to recover"
    print(f"✓ Recovery check: {recovery_result.can_recover}")
    
    print("\n✅ All GUI backend tests passed!")
    print("\nTo test the GUI interface, run:")
    print("  python run_gui.py")

if __name__ == "__main__":
    test_gui_backend()
