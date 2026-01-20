"""CLI interface for Personal Life Orchestrator (PLO).

This module provides command-line interface for PLO operations including
scenario execution, system evaluation with authority, and scenario validation.

Requirements: 11.1, 11.2, 11.3, 11.4, 11.5
"""

import argparse
import sys
from pathlib import Path
from typing import List, NoReturn

from pl_dss.config import Config, ConfigurationError, load_config
from pl_dss.evaluator import StateInputs, ValidationError, evaluate_state
from pl_dss.rules import get_active_rules
from pl_dss.authority import derive_authority
from pl_dss.scenario_runner import (
    Scenario,
    ScenarioResult,
    ScenarioError,
    load_scenarios,
    run_scenario,
    format_scenario_output,
    validate_scenario_output
)


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for PLO CLI.
    
    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        prog='plo',
        description='Personal Life Orchestrator - Safety-first personal autonomous system',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s scenario run --name "Sudden Load Spike" --file scenarios/test_scenarios.yaml
  %(prog)s scenario run-all --file scenarios/test_scenarios.yaml
  %(prog)s evaluate --deadlines 4 --domains 3 --energy 2 3 2
  %(prog)s scenario validate --file scenarios/test_scenarios.yaml
        """
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        metavar='PATH',
        help='Path to configuration file (default: config.yaml)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scenario subcommand
    scenario_parser = subparsers.add_parser('scenario', help='Scenario operations')
    scenario_subparsers = scenario_parser.add_subparsers(dest='scenario_command', help='Scenario commands')
    
    # scenario run command
    run_parser = scenario_subparsers.add_parser('run', help='Run a single scenario')
    run_parser.add_argument(
        '--name',
        type=str,
        required=True,
        metavar='NAME',
        help='Name of the scenario to run'
    )
    run_parser.add_argument(
        '--file',
        type=str,
        default='scenarios/test_scenarios.yaml',
        metavar='PATH',
        help='Path to scenario file (default: scenarios/test_scenarios.yaml)'
    )
    
    # scenario run-all command
    run_all_parser = scenario_subparsers.add_parser('run-all', help='Run all scenarios')
    run_all_parser.add_argument(
        '--file',
        type=str,
        default='scenarios/test_scenarios.yaml',
        metavar='PATH',
        help='Path to scenario file (default: scenarios/test_scenarios.yaml)'
    )
    
    # scenario validate command
    validate_parser = scenario_subparsers.add_parser('validate', help='Validate scenario file')
    validate_parser.add_argument(
        '--file',
        type=str,
        required=True,
        metavar='PATH',
        help='Path to scenario file to validate'
    )
    
    # evaluate command
    evaluate_parser = subparsers.add_parser('evaluate', help='Evaluate current state with authority')
    evaluate_parser.add_argument(
        '--deadlines',
        type=int,
        required=True,
        metavar='N',
        help='Number of fixed deadlines in next 14 days'
    )
    evaluate_parser.add_argument(
        '--domains',
        type=int,
        required=True,
        metavar='N',
        help='Number of active high-load domains'
    )
    evaluate_parser.add_argument(
        '--energy',
        type=int,
        nargs=3,
        required=True,
        metavar='SCORE',
        help='Energy scores for last 3 days (1-5 scale)'
    )
    
    # validate-v03 command
    validate_v03_parser = subparsers.add_parser('validate-v03', help='Run v0.3 validation test suite')
    validate_v03_parser.add_argument(
        '--dimension',
        type=str,
        choices=['decision-core', 'authority', 'containment', 'advisory', 'safety-boundary'],
        metavar='DIM',
        help='Run tests for specific dimension only'
    )
    validate_v03_parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed test output'
    )
    
    return parser


def cmd_scenario_run(args: argparse.Namespace, config: Config) -> int:
    """Execute 'scenario run' command.
    
    Runs a single scenario by name and outputs the result.
    
    Args:
        args: Parsed command-line arguments
        config: System configuration
        
    Returns:
        Exit code (0 for success, non-zero for error)
        
    Requirements: 11.1, 11.4, 11.5
    """
    try:
        # Load scenarios from file
        scenarios = load_scenarios(args.file)
        
        # Find the requested scenario
        scenario = None
        for s in scenarios:
            if s.name == args.name:
                scenario = s
                break
        
        if scenario is None:
            print(f"ERROR: Scenario not found: {args.name}", file=sys.stderr)
            print(f"Available scenarios in {args.file}:", file=sys.stderr)
            for s in scenarios:
                print(f"  - {s.name}", file=sys.stderr)
            return 1
        
        # Run the scenario
        result = run_scenario(scenario, config)
        
        # Format and output result
        output = format_scenario_output(result)
        print(output)
        
        return 0
        
    except ScenarioError as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: Unexpected error\nDetails: {str(e)}", file=sys.stderr)
        return 1


def cmd_scenario_run_all(args: argparse.Namespace, config: Config) -> int:
    """Execute 'scenario run-all' command.
    
    Runs all scenarios in the file and outputs results.
    If any scenario has expected output, validates against it.
    
    Args:
        args: Parsed command-line arguments
        config: System configuration
        
    Returns:
        Exit code (0 for success, non-zero if any validation fails)
        
    Requirements: 11.2, 11.4, 11.5
    """
    try:
        # Load scenarios from file
        scenarios = load_scenarios(args.file)
        
        # Run all scenarios
        results = []
        validation_failures = []
        
        for scenario in scenarios:
            try:
                result = run_scenario(scenario, config)
                results.append(result)
                
                # Validate if expected output is defined
                if scenario.expected is not None:
                    validation = validate_scenario_output(scenario, result)
                    if not validation.passed:
                        validation_failures.append((scenario.name, validation.mismatches))
                
            except ScenarioError as e:
                print(f"ERROR: Failed to run scenario '{scenario.name}'", file=sys.stderr)
                print(f"Details: {str(e)}", file=sys.stderr)
                return 1
        
        # Output all results
        for i, result in enumerate(results):
            if i > 0:
                print()  # Blank line between scenarios
            output = format_scenario_output(result)
            print(output)
        
        # Report validation failures if any
        if validation_failures:
            print("\n" + "=" * 60, file=sys.stderr)
            print("VALIDATION FAILURES:", file=sys.stderr)
            print("=" * 60, file=sys.stderr)
            for scenario_name, mismatches in validation_failures:
                print(f"\nScenario: {scenario_name}", file=sys.stderr)
                for mismatch in mismatches:
                    print(f"  - {mismatch}", file=sys.stderr)
            return 1
        
        return 0
        
    except ScenarioError as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: Unexpected error\nDetails: {str(e)}", file=sys.stderr)
        return 1


def cmd_scenario_validate(args: argparse.Namespace, config: Config) -> int:
    """Execute 'scenario validate' command.
    
    Validates scenario file structure without running scenarios.
    
    Args:
        args: Parsed command-line arguments
        config: System configuration (not used but kept for consistency)
        
    Returns:
        Exit code (0 for success, non-zero for error)
        
    Requirements: 11.3, 11.4, 11.5
    """
    try:
        # Attempt to load scenarios
        scenarios = load_scenarios(args.file)
        
        # Output validation success
        print(f"Scenario file is valid: {args.file}")
        print(f"Found {len(scenarios)} scenario(s):")
        for scenario in scenarios:
            has_expected = "with expected output" if scenario.expected else "without expected output"
            print(f"  - {scenario.name} ({has_expected})")
        
        return 0
        
    except ScenarioError as e:
        print(f"ERROR: Scenario file validation failed", file=sys.stderr)
        print(f"File: {args.file}", file=sys.stderr)
        print(f"Details: {str(e)}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: Unexpected error\nDetails: {str(e)}", file=sys.stderr)
        return 1


def cmd_evaluate(args: argparse.Namespace, config: Config) -> int:
    """Execute 'evaluate' command.
    
    Evaluates current state with authority derivation.
    
    Args:
        args: Parsed command-line arguments
        config: System configuration
        
    Returns:
        Exit code (0 for success, non-zero for error)
        
    Requirements: 11.3, 11.4, 11.5
    """
    try:
        # Create state inputs
        inputs = StateInputs(
            fixed_deadlines_14d=args.deadlines,
            active_high_load_domains=args.domains,
            energy_scores_last_3_days=args.energy
        )
        
        # Evaluate state
        state_result = evaluate_state(inputs, config)
        
        # Get active rules
        rule_result = get_active_rules(state_result.state, config)
        
        # Derive authority
        authority = derive_authority(state_result, rule_result)
        
        # Format output (similar to scenario output but without scenario name)
        lines = []
        lines.append("STATE: " + authority.state)
        lines.append("AUTHORITY:")
        lines.append(f"- planning: {authority.planning}")
        lines.append(f"- execution: {authority.execution}")
        lines.append(f"MODE: {authority.mode}")
        lines.append("ACTIVE RULES:")
        if authority.active_rules:
            for rule in authority.active_rules:
                lines.append(f"- {rule}")
        else:
            lines.append("(none)")
        
        output = "\n".join(lines)
        print(output)
        
        return 0
        
    except ValidationError as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: Unexpected error\nDetails: {str(e)}", file=sys.stderr)
        return 1


def cmd_validate_v03(args: argparse.Namespace, config: Config) -> int:
    """Execute 'validate-v03' command.
    
    Runs v0.3 validation test suite covering 5 core dimensions.
    
    Args:
        args: Parsed command-line arguments
        config: System configuration (not used but kept for consistency)
        
    Returns:
        Exit code (0 if all tests pass, non-zero if any fail)
    """
    import subprocess
    
    # Build pytest command
    pytest_args = ['python', '-m', 'pytest', 'tests/test_v03_validation.py']
    
    # Add dimension filter if specified
    if args.dimension:
        dimension_map = {
            'decision-core': 'TestDecisionCore',
            'authority': 'TestAuthority',
            'containment': 'TestContainment',
            'advisory': 'TestAdvisory',
            'safety-boundary': 'TestSafetyBoundary'
        }
        test_class = dimension_map[args.dimension]
        pytest_args.extend(['-k', test_class])
    
    # Add verbosity
    if args.verbose:
        pytest_args.append('-v')
    else:
        pytest_args.append('-q')
    
    # Run pytest
    try:
        result = subprocess.run(pytest_args, capture_output=True, text=True)
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        # Print summary
        if result.returncode == 0:
            print("\n" + "=" * 70)
            print("v0.3 VALIDATION: ALL TESTS PASSED")
            print("=" * 70)
            print("\n5 Core Dimensions Validated:")
            print("  ✓ Dimension 1: Decision Core - 状态判定正确性")
            print("  ✓ Dimension 2: Authority - 权限随状态变化")
            print("  ✓ Dimension 3: Containment - 系统拒绝能力")
            print("  ✓ Dimension 4: L1 Advisory - 建议功能")
            print("  ✓ Dimension 5: Safety Boundary - 安全边界")
            print()
        
        return result.returncode
        
    except Exception as e:
        print(f"ERROR: Failed to run validation tests", file=sys.stderr)
        print(f"Details: {str(e)}", file=sys.stderr)
        return 1


def main() -> NoReturn:
    """Main entry point for PLO CLI.
    
    Parses arguments, loads configuration, and dispatches to appropriate command handler.
    
    Requirements: 11.1, 11.2, 11.3, 11.4, 11.5
    """
    parser = create_parser()
    args = parser.parse_args()
    
    # Check if command was provided
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    # Check if scenario subcommand was provided
    if args.command == 'scenario' and args.scenario_command is None:
        parser.parse_args(['scenario', '--help'])
        sys.exit(1)
    
    try:
        # Load configuration
        config = load_config(args.config)
        
        # Dispatch to appropriate command handler
        if args.command == 'scenario':
            if args.scenario_command == 'run':
                exit_code = cmd_scenario_run(args, config)
            elif args.scenario_command == 'run-all':
                exit_code = cmd_scenario_run_all(args, config)
            elif args.scenario_command == 'validate':
                exit_code = cmd_scenario_validate(args, config)
            else:
                parser.print_help()
                exit_code = 1
        elif args.command == 'evaluate':
            exit_code = cmd_evaluate(args, config)
        elif args.command == 'validate-v03':
            exit_code = cmd_validate_v03(args, config)
        else:
            parser.print_help()
            exit_code = 1
        
        sys.exit(exit_code)
        
    except ConfigurationError as e:
        print(f"ERROR: Configuration error", file=sys.stderr)
        print(f"Details: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"ERROR: Unexpected error\nDetails: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
