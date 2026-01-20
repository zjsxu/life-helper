"""Unit tests for CLI commands.

Tests that each CLI command exists, works correctly, and returns appropriate
exit codes for success and error cases.

Requirements: 11.1, 11.2, 11.3, 11.5
"""

import sys
import pytest
from io import StringIO
from unittest.mock import patch, MagicMock
from pathlib import Path

from pl_dss.plo_cli import (
    create_parser,
    cmd_scenario_run,
    cmd_scenario_run_all,
    cmd_scenario_validate,
    cmd_evaluate,
    main
)
from pl_dss.config import load_config


@pytest.fixture
def config():
    """Load test configuration."""
    return load_config('config.yaml')


@pytest.fixture
def test_scenario_file():
    """Path to test scenario file."""
    return 'scenarios/test_scenarios.yaml'


class TestParserCreation:
    """Tests for CLI parser creation."""
    
    def test_parser_exists(self):
        """Test that the parser can be created.
        
        Requirements: 11.1, 11.2, 11.3
        """
        parser = create_parser()
        assert parser is not None
        assert parser.prog == 'plo'
    
    def test_parser_has_all_commands(self):
        """Test that parser has all required commands.
        
        Requirements: 11.1, 11.2, 11.3
        """
        parser = create_parser()
        
        # Test scenario run command
        args = parser.parse_args(['scenario', 'run', '--name', 'test', '--file', 'test.yaml'])
        assert args.command == 'scenario'
        assert args.scenario_command == 'run'
        assert args.name == 'test'
        
        # Test scenario run-all command
        args = parser.parse_args(['scenario', 'run-all', '--file', 'test.yaml'])
        assert args.command == 'scenario'
        assert args.scenario_command == 'run-all'
        
        # Test scenario validate command
        args = parser.parse_args(['scenario', 'validate', '--file', 'test.yaml'])
        assert args.command == 'scenario'
        assert args.scenario_command == 'validate'
        
        # Test evaluate command
        args = parser.parse_args(['evaluate', '--deadlines', '3', '--domains', '2', '--energy', '4', '4', '5'])
        assert args.command == 'evaluate'
        assert args.deadlines == 3
        assert args.domains == 2
        assert args.energy == [4, 4, 5]


class TestScenarioRunCommand:
    """Tests for 'scenario run' command.
    
    Requirements: 11.1, 11.4, 11.5
    """
    
    def test_scenario_run_success(self, config, test_scenario_file, capsys):
        """Test successful scenario run returns exit code 0."""
        parser = create_parser()
        args = parser.parse_args(['scenario', 'run', '--name', 'Sudden Load Spike', '--file', test_scenario_file])
        
        exit_code = cmd_scenario_run(args, config)
        
        assert exit_code == 0
        
        # Verify output was written to stdout
        captured = capsys.readouterr()
        assert 'SCENARIO: Sudden Load Spike' in captured.out
        assert 'STATE: OVERLOADED' in captured.out
    
    def test_scenario_run_not_found(self, config, test_scenario_file, capsys):
        """Test scenario run with non-existent scenario returns exit code 1."""
        parser = create_parser()
        args = parser.parse_args(['scenario', 'run', '--name', 'NonExistent', '--file', test_scenario_file])
        
        exit_code = cmd_scenario_run(args, config)
        
        assert exit_code == 1
        
        # Verify error was written to stderr
        captured = capsys.readouterr()
        assert 'ERROR: Scenario not found' in captured.err
    
    def test_scenario_run_invalid_file(self, config, capsys):
        """Test scenario run with invalid file returns exit code 1."""
        parser = create_parser()
        args = parser.parse_args(['scenario', 'run', '--name', 'test', '--file', 'nonexistent.yaml'])
        
        exit_code = cmd_scenario_run(args, config)
        
        assert exit_code == 1
        
        # Verify error was written to stderr
        captured = capsys.readouterr()
        assert 'ERROR:' in captured.err


class TestScenarioRunAllCommand:
    """Tests for 'scenario run-all' command.
    
    Requirements: 11.2, 11.4, 11.5
    """
    
    def test_scenario_run_all_success(self, config, test_scenario_file, capsys):
        """Test successful run-all returns exit code 0."""
        parser = create_parser()
        args = parser.parse_args(['scenario', 'run-all', '--file', test_scenario_file])
        
        exit_code = cmd_scenario_run_all(args, config)
        
        assert exit_code == 0
        
        # Verify multiple scenarios were output
        captured = capsys.readouterr()
        assert 'SCENARIO: Sudden Load Spike' in captured.out
        assert 'SCENARIO: Gradual Stress' in captured.out
        assert 'SCENARIO: Normal Operation' in captured.out
    
    def test_scenario_run_all_invalid_file(self, config, capsys):
        """Test run-all with invalid file returns exit code 1."""
        parser = create_parser()
        args = parser.parse_args(['scenario', 'run-all', '--file', 'nonexistent.yaml'])
        
        exit_code = cmd_scenario_run_all(args, config)
        
        assert exit_code == 1
        
        # Verify error was written to stderr
        captured = capsys.readouterr()
        assert 'ERROR:' in captured.err


class TestScenarioValidateCommand:
    """Tests for 'scenario validate' command.
    
    Requirements: 11.3, 11.4, 11.5
    """
    
    def test_scenario_validate_success(self, config, test_scenario_file, capsys):
        """Test successful validation returns exit code 0."""
        parser = create_parser()
        args = parser.parse_args(['scenario', 'validate', '--file', test_scenario_file])
        
        exit_code = cmd_scenario_validate(args, config)
        
        assert exit_code == 0
        
        # Verify success message was written to stdout
        captured = capsys.readouterr()
        assert 'Scenario file is valid' in captured.out
        assert test_scenario_file in captured.out
    
    def test_scenario_validate_invalid_file(self, config, capsys):
        """Test validation with invalid file returns exit code 1."""
        parser = create_parser()
        args = parser.parse_args(['scenario', 'validate', '--file', 'nonexistent.yaml'])
        
        exit_code = cmd_scenario_validate(args, config)
        
        assert exit_code == 1
        
        # Verify error was written to stderr
        captured = capsys.readouterr()
        assert 'ERROR:' in captured.err
        assert 'validation failed' in captured.err


class TestEvaluateCommand:
    """Tests for 'evaluate' command.
    
    Requirements: 11.3, 11.4, 11.5
    """
    
    def test_evaluate_success(self, config, capsys):
        """Test successful evaluation returns exit code 0."""
        parser = create_parser()
        args = parser.parse_args(['evaluate', '--deadlines', '4', '--domains', '3', '--energy', '2', '2', '2'])
        
        exit_code = cmd_evaluate(args, config)
        
        assert exit_code == 0
        
        # Verify output was written to stdout
        captured = capsys.readouterr()
        assert 'STATE: OVERLOADED' in captured.out
        assert 'AUTHORITY:' in captured.out
        assert 'planning: DENIED' in captured.out
        assert 'execution: DENIED' in captured.out
    
    def test_evaluate_normal_state(self, config, capsys):
        """Test evaluation with normal state inputs."""
        parser = create_parser()
        args = parser.parse_args(['evaluate', '--deadlines', '1', '--domains', '1', '--energy', '4', '4', '5'])
        
        exit_code = cmd_evaluate(args, config)
        
        assert exit_code == 0
        
        # Verify normal state output
        captured = capsys.readouterr()
        assert 'STATE: NORMAL' in captured.out
        assert 'planning: ALLOWED' in captured.out
        assert 'execution: DENIED' in captured.out
    
    def test_evaluate_invalid_energy_scores(self, config, capsys):
        """Test evaluation with invalid energy scores returns exit code 1."""
        parser = create_parser()
        args = parser.parse_args(['evaluate', '--deadlines', '1', '--domains', '1', '--energy', '0', '0', '0'])
        
        exit_code = cmd_evaluate(args, config)
        
        assert exit_code == 1
        
        # Verify error was written to stderr
        captured = capsys.readouterr()
        assert 'ERROR:' in captured.err


class TestMainFunction:
    """Tests for main entry point.
    
    Requirements: 11.1, 11.2, 11.3, 11.4, 11.5
    """
    
    def test_main_no_command_exits_with_error(self):
        """Test main with no command exits with code 1."""
        with patch('sys.argv', ['plo']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
    
    def test_main_scenario_run_success(self):
        """Test main with scenario run command exits with code 0."""
        with patch('sys.argv', ['plo', 'scenario', 'run', '--name', 'Sudden Load Spike', '--file', 'scenarios/test_scenarios.yaml']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
    
    def test_main_evaluate_success(self):
        """Test main with evaluate command exits with code 0."""
        with patch('sys.argv', ['plo', 'evaluate', '--deadlines', '1', '--domains', '1', '--energy', '4', '4', '5']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
    
    def test_main_invalid_config_exits_with_error(self):
        """Test main with invalid config file exits with code 1."""
        with patch('sys.argv', ['plo', '--config', 'nonexistent.yaml', 'evaluate', '--deadlines', '1', '--domains', '1', '--energy', '4', '4', '5']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
    
    def test_main_keyboard_interrupt_exits_with_130(self):
        """Test main handles KeyboardInterrupt with exit code 130."""
        with patch('sys.argv', ['plo', 'evaluate', '--deadlines', '1', '--domains', '1', '--energy', '4', '4', '5']):
            with patch('pl_dss.plo_cli.load_config', side_effect=KeyboardInterrupt()):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 130


class TestExitCodes:
    """Tests for exit code consistency.
    
    Requirements: 11.5
    """
    
    def test_all_success_cases_return_zero(self, config, test_scenario_file):
        """Test that all successful operations return exit code 0."""
        parser = create_parser()
        
        # scenario run success
        args = parser.parse_args(['scenario', 'run', '--name', 'Sudden Load Spike', '--file', test_scenario_file])
        assert cmd_scenario_run(args, config) == 0
        
        # scenario run-all success
        args = parser.parse_args(['scenario', 'run-all', '--file', test_scenario_file])
        assert cmd_scenario_run_all(args, config) == 0
        
        # scenario validate success
        args = parser.parse_args(['scenario', 'validate', '--file', test_scenario_file])
        assert cmd_scenario_validate(args, config) == 0
        
        # evaluate success
        args = parser.parse_args(['evaluate', '--deadlines', '1', '--domains', '1', '--energy', '4', '4', '5'])
        assert cmd_evaluate(args, config) == 0
    
    def test_all_error_cases_return_nonzero(self, config):
        """Test that all error cases return non-zero exit codes."""
        parser = create_parser()
        
        # scenario run with non-existent scenario
        args = parser.parse_args(['scenario', 'run', '--name', 'NonExistent', '--file', 'scenarios/test_scenarios.yaml'])
        assert cmd_scenario_run(args, config) != 0
        
        # scenario run-all with invalid file
        args = parser.parse_args(['scenario', 'run-all', '--file', 'nonexistent.yaml'])
        assert cmd_scenario_run_all(args, config) != 0
        
        # scenario validate with invalid file
        args = parser.parse_args(['scenario', 'validate', '--file', 'nonexistent.yaml'])
        assert cmd_scenario_validate(args, config) != 0
        
        # evaluate with invalid energy scores
        args = parser.parse_args(['evaluate', '--deadlines', '1', '--domains', '1', '--energy', '0', '0', '0'])
        assert cmd_evaluate(args, config) != 0
