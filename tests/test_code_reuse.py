"""
Unit tests for code reuse validation.

Tests that the glue script properly reuses existing functions from the
Decision Core and does not duplicate logic or hardcode configuration values.

Requirements: 5.7, 5.8, 11.5, 18.4
"""

import ast
import os
import pytest


class TestCodeReuse:
    """Test that glue script reuses existing system functions."""
    
    @pytest.fixture
    def glue_script_path(self):
        """Get path to glue script."""
        return os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "scripts", 
            "run_from_issue.py"
        )
    
    @pytest.fixture
    def glue_script_content(self, glue_script_path):
        """Load glue script content."""
        with open(glue_script_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @pytest.fixture
    def glue_script_ast(self, glue_script_content):
        """Parse glue script into AST."""
        return ast.parse(glue_script_content)
    
    def test_glue_script_imports_evaluate_state(self, glue_script_content):
        """
        Test that glue script imports evaluate_state from evaluator.
        
        Validates: Requirement 5.7 - Glue_Script SHALL NOT modify Decision Core logic
        """
        assert "from pl_dss.evaluator import" in glue_script_content, \
            "Glue script must import from pl_dss.evaluator"
        assert "evaluate_state" in glue_script_content, \
            "Glue script must import evaluate_state function"
    
    def test_glue_script_imports_derive_authority(self, glue_script_content):
        """
        Test that glue script imports derive_authority from authority.
        
        Validates: Requirement 5.8 - Glue_Script SHALL NOT modify Global Authority logic
        """
        assert "from pl_dss.authority import" in glue_script_content, \
            "Glue script must import from pl_dss.authority"
        assert "derive_authority" in glue_script_content, \
            "Glue script must import derive_authority function"
    
    def test_glue_script_imports_format_output(self, glue_script_content):
        """
        Test that glue script imports format_output from main.
        
        Validates: Requirement 18.2 - Glue_Script SHALL reuse existing format_output function
        """
        assert "from pl_dss.main import" in glue_script_content, \
            "Glue script must import from pl_dss.main"
        assert "format_output" in glue_script_content, \
            "Glue script must import format_output function"
    
    def test_glue_script_imports_load_config(self, glue_script_content):
        """
        Test that glue script imports load_config from config.
        
        Validates: Requirement 18.4 - System SHALL use same configuration file (config.yaml)
        """
        assert "from pl_dss.config import" in glue_script_content, \
            "Glue script must import from pl_dss.config"
        assert "load_config" in glue_script_content, \
            "Glue script must import load_config function"
    
    def test_glue_script_imports_check_recovery(self, glue_script_content):
        """
        Test that glue script imports check_recovery from recovery.
        
        Validates: Requirement 5.5 - Glue_Script SHALL call Recovery monitor
        """
        assert "from pl_dss.recovery import" in glue_script_content, \
            "Glue script must import from pl_dss.recovery"
        assert "check_recovery" in glue_script_content, \
            "Glue script must import check_recovery function"
    
    def test_glue_script_imports_get_active_rules(self, glue_script_content):
        """
        Test that glue script imports get_active_rules from rules.
        
        Validates: Requirement 5.4 - Glue_Script SHALL call Decision Core evaluator
        """
        assert "from pl_dss.rules import" in glue_script_content, \
            "Glue script must import from pl_dss.rules"
        assert "get_active_rules" in glue_script_content, \
            "Glue script must import get_active_rules function"
    
    def test_glue_script_uses_config_yaml(self, glue_script_content):
        """
        Test that glue script loads config.yaml (not hardcoded values).
        
        Validates: Requirement 18.4 - System SHALL use same configuration file
        """
        # Check that load_config is called with 'config.yaml'
        assert "load_config('config.yaml')" in glue_script_content or \
               'load_config("config.yaml")' in glue_script_content, \
            "Glue script must call load_config('config.yaml')"
    
    def test_glue_script_calls_evaluate_state(self, glue_script_content):
        """
        Test that glue script calls evaluate_state function.
        
        Validates: Requirement 5.3 - Glue_Script SHALL call Decision Core evaluator
        """
        assert "evaluate_state(" in glue_script_content, \
            "Glue script must call evaluate_state function"
    
    def test_glue_script_calls_derive_authority(self, glue_script_content):
        """
        Test that glue script calls derive_authority function.
        
        Validates: Requirement 5.4 - Glue_Script SHALL call Global Authority derivation
        """
        assert "derive_authority(" in glue_script_content, \
            "Glue script must call derive_authority function"
    
    def test_glue_script_calls_check_recovery(self, glue_script_content):
        """
        Test that glue script calls check_recovery function.
        
        Validates: Requirement 5.5 - Glue_Script SHALL call Recovery monitor
        """
        assert "check_recovery(" in glue_script_content, \
            "Glue script must call check_recovery function"
    
    def test_glue_script_calls_format_output(self, glue_script_content):
        """
        Test that glue script calls format_output function.
        
        Validates: Requirement 5.6 - Glue_Script SHALL output results in deterministic CLI format
        """
        assert "format_output(" in glue_script_content, \
            "Glue script must call format_output function"
    
    def test_glue_script_no_hardcoded_thresholds(self, glue_script_content):
        """
        Test that glue script does not contain hardcoded threshold values.
        
        Validates: Requirement 11.5 - System SHALL reuse existing Decision Core validation logic
        """
        # Check for common threshold patterns that would indicate hardcoding
        # These are the actual threshold values from config.yaml
        hardcoded_patterns = [
            "fixed_deadlines >= 3",
            "active_domains >= 2",
            "energy_avg <= 2.5",
            "2.5",  # Energy threshold
        ]
        
        # Allow these patterns in comments/docstrings but not in code
        lines = glue_script_content.split('\n')
        code_lines = [
            line for line in lines 
            if not line.strip().startswith('#') and 
               not line.strip().startswith('"""') and
               not line.strip().startswith("'''")
        ]
        code_only = '\n'.join(code_lines)
        
        # Check that threshold values are not hardcoded in actual code
        # (They should come from config)
        for pattern in [">= 3", ">= 2", "<= 2.5"]:
            assert pattern not in code_only, \
                f"Glue script should not hardcode threshold values like '{pattern}'"
    
    def test_glue_script_no_duplicate_state_evaluation(self, glue_script_content):
        """
        Test that glue script does not duplicate state evaluation logic.
        
        Validates: Requirement 5.7 - Glue_Script SHALL NOT modify Decision Core logic
        """
        # Check that glue script doesn't implement its own state evaluation
        forbidden_patterns = [
            "def evaluate_state",  # Redefining the function
            "if fixed_deadlines_14d >=",  # Implementing threshold checks
            "if active_high_load_domains >=",  # Implementing threshold checks
            "if energy_avg <=",  # Implementing threshold checks
        ]
        
        for pattern in forbidden_patterns:
            assert pattern not in glue_script_content, \
                f"Glue script should not duplicate state evaluation logic: '{pattern}'"
    
    def test_glue_script_no_duplicate_authority_logic(self, glue_script_content):
        """
        Test that glue script does not duplicate authority derivation logic.
        
        Validates: Requirement 5.8 - Glue_Script SHALL NOT modify Global Authority logic
        """
        # Check that glue script doesn't implement its own authority logic
        # We need to check actual code, not documentation/comments
        
        # Split into lines and filter out docstrings and comments
        lines = glue_script_content.split('\n')
        code_lines = []
        in_docstring = False
        docstring_char = None
        
        for line in lines:
            stripped = line.strip()
            
            # Track docstring state (both """ and ''')
            if '"""' in stripped:
                if docstring_char == '"""' or docstring_char is None:
                    in_docstring = not in_docstring
                    docstring_char = '"""' if in_docstring else None
                continue
            elif "'''" in stripped:
                if docstring_char == "'''" or docstring_char is None:
                    in_docstring = not in_docstring
                    docstring_char = "'''" if in_docstring else None
                continue
            
            # Skip comments and docstrings
            if not in_docstring and not stripped.startswith('#'):
                code_lines.append(line)
        
        code_only = '\n'.join(code_lines)
        
        # Check for forbidden patterns in actual code
        forbidden_patterns = [
            "def derive_authority",  # Redefining the function
            'authority.planning = "ALLOWED"',  # Modifying authority object
            'authority.planning = "DENIED"',  # Modifying authority object
            'authority.execution = "ALLOWED"',  # Modifying authority object
        ]
        
        for pattern in forbidden_patterns:
            assert pattern not in code_only, \
                f"Glue script should not duplicate authority logic: '{pattern}'"
    
    def test_glue_script_imports_state_inputs(self, glue_script_content):
        """
        Test that glue script imports StateInputs dataclass.
        
        Validates: Requirement 5.2 - Glue_Script SHALL parse Issue body into StateInputs
        """
        assert "StateInputs" in glue_script_content, \
            "Glue script must import StateInputs dataclass"
    
    def test_glue_script_creates_state_inputs(self, glue_script_content):
        """
        Test that glue script creates StateInputs objects.
        
        Validates: Requirement 5.2 - Glue_Script SHALL parse Issue body into StateInputs
        """
        assert "StateInputs(" in glue_script_content, \
            "Glue script must create StateInputs objects"


class TestConfigurationReuse:
    """Test that system uses config.yaml consistently."""
    
    def test_config_yaml_exists(self):
        """
        Test that config.yaml exists in repository root.
        
        Validates: Requirement 18.4 - System SHALL use same configuration file
        """
        config_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
        assert os.path.exists(config_path), "config.yaml must exist"
    
    def test_config_yaml_not_duplicated(self):
        """
        Test that there is only one config.yaml (no duplicates).
        
        Validates: Requirement 18.4 - System SHALL use same configuration file
        """
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Find all config.yaml files
        config_files = []
        for root, dirs, files in os.walk(repo_root):
            # Skip hidden directories and common non-source directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'venv', '__pycache__']]
            
            if 'config.yaml' in files:
                config_files.append(os.path.join(root, 'config.yaml'))
        
        assert len(config_files) == 1, \
            f"There should be exactly one config.yaml, found {len(config_files)}: {config_files}"


class TestNoCodeDuplication:
    """Test that glue script does not duplicate existing code."""
    
    @pytest.fixture
    def glue_script_content(self):
        """Load glue script content."""
        glue_script_path = os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "scripts", 
            "run_from_issue.py"
        )
        with open(glue_script_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def test_no_duplicate_format_output_logic(self, glue_script_content):
        """
        Test that glue script does not duplicate format_output logic.
        
        Validates: Requirement 18.2 - Glue_Script SHALL reuse existing format_output function
        """
        # Check for patterns that would indicate duplicating format_output
        forbidden_patterns = [
            "=== Personal Decision-Support System ===",  # Output header
            "Current State:",  # State formatting
            "Active Rules:",  # Rules formatting
        ]
        
        # These patterns should only appear in comments/docstrings, not in code
        lines = glue_script_content.split('\n')
        code_lines = []
        in_docstring = False
        
        for line in lines:
            stripped = line.strip()
            
            # Track docstring state
            if '"""' in stripped or "'''" in stripped:
                in_docstring = not in_docstring
                continue
            
            # Skip comments and docstrings
            if not in_docstring and not stripped.startswith('#'):
                code_lines.append(line)
        
        code_only = '\n'.join(code_lines)
        
        # Check that output formatting is not duplicated
        for pattern in forbidden_patterns:
            # Allow in string literals that are part of error messages
            # but not as part of output formatting
            if pattern in code_only:
                # Make sure it's not part of format_output call
                assert "format_output(" in code_only, \
                    f"If '{pattern}' appears, it should be via format_output() call"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
