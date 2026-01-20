"""
Property-based tests for frozen component immutability.

Tests that frozen components (Decision Core, Authority, Recovery, Config)
remain byte-for-byte identical to v0.3-stable tag.

Requirements: 1.5, 17.1, 17.2, 17.3, 17.4, 17.5
"""

import os
import hashlib
import subprocess
import pytest
from hypothesis import given, strategies as st, settings


# ============================================================================
# Frozen Component Paths
# ============================================================================

FROZEN_COMPONENTS = [
    "pl_dss/evaluator.py",
    "pl_dss/rules.py",
    "pl_dss/authority.py",
    "pl_dss/recovery.py",
    "config.yaml",
]


# ============================================================================
# Helper Functions
# ============================================================================

def get_file_hash(filepath: str) -> str:
    """
    Compute SHA256 hash of a file.
    
    Args:
        filepath: Path to file relative to repository root
        
    Returns:
        Hex string of SHA256 hash
    """
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(repo_root, filepath)
    
    with open(full_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def get_git_file_hash(filepath: str, tag: str = "v0.3-stable") -> str:
    """
    Get SHA256 hash of a file at a specific git tag.
    
    Args:
        filepath: Path to file relative to repository root
        tag: Git tag to check
        
    Returns:
        Hex string of SHA256 hash
        
    Raises:
        subprocess.CalledProcessError: If git command fails
    """
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Get file content at tag
    result = subprocess.run(
        ["git", "show", f"{tag}:{filepath}"],
        cwd=repo_root,
        capture_output=True,
        check=True
    )
    
    return hashlib.sha256(result.stdout).hexdigest()


def check_component_unchanged(filepath: str) -> tuple[bool, str, str]:
    """
    Check if a component file is unchanged from v0.3-stable.
    
    Args:
        filepath: Path to file relative to repository root
        
    Returns:
        Tuple of (is_unchanged, current_hash, baseline_hash)
    """
    try:
        current_hash = get_file_hash(filepath)
        baseline_hash = get_git_file_hash(filepath, "v0.3-stable")
        return (current_hash == baseline_hash, current_hash, baseline_hash)
    except subprocess.CalledProcessError:
        # If git command fails, tag might not exist
        pytest.skip(f"v0.3-stable tag not found or file {filepath} not in tag")
    except FileNotFoundError:
        pytest.fail(f"File {filepath} not found in current working directory")


# ============================================================================
# Property 1: Frozen Component Immutability
# ============================================================================

class TestFrozenComponentImmutability:
    """
    Test that frozen components remain unchanged from v0.3-stable.
    
    Feature: github-interface, Property 1: Frozen Component Immutability
    
    For any frozen component file (evaluator.py, rules.py, authority.py, 
    recovery.py, config.yaml thresholds), the file content should remain 
    byte-for-byte identical to v0.3-stable tag.
    
    Validates: Requirements 1.5, 17.1, 17.2, 17.3, 17.4, 17.5
    """
    
    def test_evaluator_unchanged(self):
        """
        Test that evaluator.py is unchanged from v0.3-stable.
        
        Validates: Requirement 17.1 - GitHub_Interface SHALL NOT modify evaluator.py logic
        """
        is_unchanged, current, baseline = check_component_unchanged("pl_dss/evaluator.py")
        
        assert is_unchanged, (
            f"evaluator.py has been modified!\n"
            f"Current hash:  {current}\n"
            f"Baseline hash: {baseline}\n"
            f"Decision Core must remain frozen."
        )
    
    def test_rules_unchanged(self):
        """
        Test that rules.py is unchanged from v0.3-stable.
        
        Validates: Requirement 17.2 - GitHub_Interface SHALL NOT modify rules.py logic
        """
        is_unchanged, current, baseline = check_component_unchanged("pl_dss/rules.py")
        
        assert is_unchanged, (
            f"rules.py has been modified!\n"
            f"Current hash:  {current}\n"
            f"Baseline hash: {baseline}\n"
            f"Decision Core rules must remain frozen."
        )
    
    def test_authority_unchanged(self):
        """
        Test that authority.py is unchanged from v0.3-stable.
        
        Validates: Requirement 17.3 - GitHub_Interface SHALL NOT modify authority.py logic
        """
        is_unchanged, current, baseline = check_component_unchanged("pl_dss/authority.py")
        
        assert is_unchanged, (
            f"authority.py has been modified!\n"
            f"Current hash:  {current}\n"
            f"Baseline hash: {baseline}\n"
            f"Global Authority must remain frozen."
        )
    
    def test_recovery_unchanged(self):
        """
        Test that recovery.py is unchanged from v0.3-stable.
        
        Validates: Requirement 17.4 - GitHub_Interface SHALL NOT modify recovery.py logic
        """
        is_unchanged, current, baseline = check_component_unchanged("pl_dss/recovery.py")
        
        assert is_unchanged, (
            f"recovery.py has been modified!\n"
            f"Current hash:  {current}\n"
            f"Baseline hash: {baseline}\n"
            f"Recovery monitoring must remain frozen."
        )
    
    def test_config_unchanged(self):
        """
        Test that config.yaml is unchanged from v0.3-stable.
        
        Validates: Requirement 17.5 - GitHub_Interface SHALL NOT modify containment thresholds
        """
        is_unchanged, current, baseline = check_component_unchanged("config.yaml")
        
        assert is_unchanged, (
            f"config.yaml has been modified!\n"
            f"Current hash:  {current}\n"
            f"Baseline hash: {baseline}\n"
            f"Configuration thresholds must remain frozen."
        )
    
    @given(component=st.sampled_from(FROZEN_COMPONENTS))
    @settings(max_examples=100)
    def test_all_frozen_components_unchanged_property(self, component: str):
        """
        Property test: All frozen components remain unchanged.
        
        Feature: github-interface, Property 1: Frozen Component Immutability
        
        For any frozen component file, the file content should remain 
        byte-for-byte identical to v0.3-stable tag.
        
        Validates: Requirements 1.5, 17.1, 17.2, 17.3, 17.4, 17.5
        """
        is_unchanged, current, baseline = check_component_unchanged(component)
        
        assert is_unchanged, (
            f"{component} has been modified!\n"
            f"Current hash:  {current}\n"
            f"Baseline hash: {baseline}\n"
            f"Frozen components must remain unchanged from v0.3-stable."
        )


# ============================================================================
# Additional Validation Tests
# ============================================================================

class TestGitTagExists:
    """Test that v0.3-stable tag exists."""
    
    def test_v03_stable_tag_exists(self):
        """
        Test that v0.3-stable git tag exists.
        
        Validates: Requirement 1.1 - System SHALL create git tag marking frozen state
        """
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        result = subprocess.run(
            ["git", "tag", "-l", "v0.3-stable"],
            cwd=repo_root,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, "Git command failed"
        assert "v0.3-stable" in result.stdout, "v0.3-stable tag does not exist"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
