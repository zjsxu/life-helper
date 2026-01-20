"""Main controller for PL-DSS."""

import argparse
import sys
from typing import Optional

from pl_dss.config import Config, ConfigurationError, load_config
from pl_dss.evaluator import StateInputs, StateResult, ValidationError, evaluate_state
from pl_dss.recovery import RecoveryResult, check_recovery
from pl_dss.rules import RuleResult, get_active_rules


def parse_arguments() -> Optional[StateInputs]:
    """Parse command-line arguments for system inputs.
    
    Returns:
        StateInputs if all arguments provided, None if interactive mode needed
    """
    parser = argparse.ArgumentParser(
        description="Personal Life Decision-Support System (PL-DSS)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --deadlines 4 --domains 3 --energy 2 3 2
  %(prog)s  (interactive mode)
        """
    )
    
    parser.add_argument(
        '--deadlines',
        type=int,
        metavar='N',
        help='Number of fixed deadlines in next 14 days'
    )
    
    parser.add_argument(
        '--domains',
        type=int,
        metavar='N',
        help='Number of active high-load domains'
    )
    
    parser.add_argument(
        '--energy',
        type=int,
        nargs=3,
        metavar='SCORE',
        help='Energy scores for last 3 days (1-5 scale)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        metavar='PATH',
        help='Path to configuration file (default: config.yaml)'
    )
    
    args = parser.parse_args()
    
    # If all inputs provided via CLI, return StateInputs
    if args.deadlines is not None and args.domains is not None and args.energy is not None:
        return StateInputs(
            fixed_deadlines_14d=args.deadlines,
            active_high_load_domains=args.domains,
            energy_scores_last_3_days=args.energy
        )
    
    # If some but not all inputs provided, show error
    if any([args.deadlines is not None, args.domains is not None, args.energy is not None]):
        parser.error("All inputs (--deadlines, --domains, --energy) must be provided together")
    
    # No inputs provided, return None for interactive mode
    return None


def prompt_for_inputs() -> StateInputs:
    """Prompt user for inputs interactively.
    
    Returns:
        StateInputs with user-provided data
    """
    print("=== Personal Decision-Support System ===\n")
    print("Please provide the following information:\n")
    
    # Prompt for fixed deadlines
    while True:
        try:
            deadlines_str = input("Number of fixed deadlines in next 14 days: ").strip()
            deadlines = int(deadlines_str)
            if deadlines < 0:
                print("Error: Must be a non-negative integer. Try again.\n")
                continue
            break
        except ValueError:
            print("Error: Must be a valid integer. Try again.\n")
    
    # Prompt for high-load domains
    while True:
        try:
            domains_str = input("Number of active high-load domains: ").strip()
            domains = int(domains_str)
            if domains < 0:
                print("Error: Must be a non-negative integer. Try again.\n")
                continue
            break
        except ValueError:
            print("Error: Must be a valid integer. Try again.\n")
    
    # Prompt for energy scores
    while True:
        try:
            energy_str = input("Energy scores for last 3 days (space-separated, 1-5 scale): ").strip()
            energy_parts = energy_str.split()
            if len(energy_parts) != 3:
                print("Error: Must provide exactly 3 scores. Try again.\n")
                continue
            energy = [int(s) for s in energy_parts]
            if any(score < 1 or score > 5 for score in energy):
                print("Error: All scores must be between 1 and 5. Try again.\n")
                continue
            break
        except ValueError:
            print("Error: Must be valid integers. Try again.\n")
    
    print()  # Blank line before output
    return StateInputs(
        fixed_deadlines_14d=deadlines,
        active_high_load_domains=domains,
        energy_scores_last_3_days=energy
    )


def run_system(inputs: StateInputs, config: Config) -> tuple[StateResult, RuleResult, RecoveryResult]:
    """Run the complete system pipeline.
    
    Args:
        inputs: User-provided state inputs
        config: System configuration
        
    Returns:
        Tuple of (state_result, rule_result, recovery_result)
        
    Raises:
        ValidationError: If inputs are invalid
    """
    # Evaluate state
    state_result = evaluate_state(inputs, config)
    
    # Get active rules
    rule_result = get_active_rules(state_result.state, config)
    
    # Check recovery status
    recovery_result = check_recovery(inputs, state_result.state, config)
    
    return state_result, rule_result, recovery_result


def format_state_result(state_result: StateResult) -> str:
    """Format state result with explanation.
    
    Args:
        state_result: StateResult from evaluator
        
    Returns:
        Formatted plain text string
    """
    output = f"Current State: {state_result.state}\n"
    output += f"Reason: {state_result.explanation}"
    return output


def format_active_rules(rule_result: RuleResult) -> str:
    """Format active rules list.
    
    Args:
        rule_result: RuleResult from rule engine
        
    Returns:
        Formatted plain text string, empty if no rules
    """
    if not rule_result.active_rules:
        return ""
    
    output = "Active Rules:\n"
    for rule in rule_result.active_rules:
        output += f"  • {rule}\n"
    return output.rstrip()  # Remove trailing newline


def format_recovery_status(recovery_result: RecoveryResult) -> str:
    """Format recovery status.
    
    Args:
        recovery_result: RecoveryResult from recovery monitor
        
    Returns:
        Formatted plain text string
    """
    status = "Ready" if recovery_result.can_recover else "Not ready"
    output = f"Recovery Status: {status}\n"
    
    if recovery_result.can_recover:
        output += "All recovery conditions met. Safe to return to NORMAL mode."
    else:
        output += "Recovery not ready. Blocking conditions:"
        for condition in recovery_result.blocking_conditions:
            output += f"\n  • {condition}"
    
    return output


def format_output(state_result: StateResult, rule_result: RuleResult, recovery_result: RecoveryResult) -> str:
    """Format complete system output.
    
    Args:
        state_result: StateResult from evaluator
        rule_result: RuleResult from rule engine
        recovery_result: RecoveryResult from recovery monitor
        
    Returns:
        Complete formatted plain text output
    """
    sections = []
    
    # Header
    sections.append("=== Personal Decision-Support System ===")
    
    # State result
    sections.append(format_state_result(state_result))
    
    # Active rules (if any)
    rules_output = format_active_rules(rule_result)
    if rules_output:
        sections.append(rules_output)
    
    # Recovery status
    sections.append(format_recovery_status(recovery_result))
    
    return "\n\n".join(sections)


def main():
    """Main entry point for the PL-DSS application."""
    try:
        # Parse command-line arguments
        args = parse_arguments()
        
        # Get config path from args if available
        config_path = 'config.yaml'
        if len(sys.argv) > 1:
            parser = argparse.ArgumentParser(add_help=False)
            parser.add_argument('--config', type=str, default='config.yaml')
            known_args, _ = parser.parse_known_args()
            config_path = known_args.config
        
        # Load configuration
        try:
            config = load_config(config_path)
        except ConfigurationError as e:
            print(str(e), file=sys.stderr)
            sys.exit(1)
        
        # Get inputs (from CLI or interactive prompt)
        if args is None:
            inputs = prompt_for_inputs()
        else:
            inputs = args
        
        # Run system pipeline
        try:
            state_result, rule_result, recovery_result = run_system(inputs, config)
        except ValidationError as e:
            print(str(e), file=sys.stderr)
            sys.exit(1)
        
        # Format and display output
        output = format_output(state_result, rule_result, recovery_result)
        print(output)
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"\nERROR: Unexpected error occurred\nDetails: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
