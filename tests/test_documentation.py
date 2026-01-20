"""
Unit tests for documentation completeness.

Tests that README and documentation contain all required sections
for the Personal Life Orchestrator (PLO) system.

Requirements: 12.1, 12.2, 12.3, 12.4, 12.5
"""

import os
import pytest


class TestDocumentation:
    """Test that documentation exists and contains required sections."""

    @pytest.fixture
    def readme_content(self):
        """Load README.md content."""
        readme_path = os.path.join(os.path.dirname(__file__), "..", "README.md")
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()

    def test_readme_exists(self):
        """Test that README.md exists.
        
        Requirement: 12.1 - System SHALL include README explaining what the system does
        """
        readme_path = os.path.join(os.path.dirname(__file__), "..", "README.md")
        assert os.path.exists(readme_path), "README.md must exist"

    def test_readme_explains_what_system_does(self, readme_content):
        """Test that README explains what the system does.
        
        Requirement: 12.1 - System SHALL include README explaining what the system does
        """
        # Check for PLO section
        assert "Personal Life Orchestrator" in readme_content or "PLO" in readme_content, \
            "README must explain Personal Life Orchestrator"
        
        # Check for explanation of what PLO does
        assert "What PLO Does" in readme_content, \
            "README must have 'What PLO Does' section"

    def test_readme_explains_what_system_refuses(self, readme_content):
        """Test that README explains what the system refuses to do.
        
        Requirement: 12.2 - System SHALL include README explaining what the system refuses to do
        """
        assert "What PLO Refuses to Do" in readme_content, \
            "README must have 'What PLO Refuses to Do' section"
        
        # Check for explicit refusals
        assert "No autonomous execution" in readme_content or "❌" in readme_content, \
            "README must list what PLO refuses to do"

    def test_readme_explains_safe_expansion(self, readme_content):
        """Test that README explains how the system will expand safely.
        
        Requirement: 12.3 - System SHALL include README explaining how it will expand safely
        """
        assert "How PLO Will Expand Safely" in readme_content, \
            "README must have 'How PLO Will Expand Safely' section"
        
        # Check for phase-based expansion
        assert "Phase" in readme_content or "phase" in readme_content, \
            "README must explain phased expansion approach"

    def test_layer_responsibilities_documented(self, readme_content):
        """Test that layer responsibilities are documented.
        
        Requirement: 12.4 - System SHALL document layer responsibilities
        """
        assert "PLO Layer Responsibilities" in readme_content or "Layer Responsibilities" in readme_content, \
            "README must have layer responsibilities section"
        
        # Check for L0, L1, L2 documentation
        assert "L0" in readme_content or "Decision Core" in readme_content, \
            "README must document L0 (Decision Core) layer"
        assert "L1" in readme_content or "Planning Engine" in readme_content, \
            "README must document L1 (Planning Engine) layer"
        assert "L2" in readme_content or "Execution Layer" in readme_content, \
            "README must document L2 (Execution Layer) layer"

    def test_l0_decision_core_documented(self, readme_content):
        """Test that L0 Decision Core responsibilities are documented.
        
        Requirement: 12.4 - System SHALL document layer responsibilities
        """
        # Check for L0 section
        assert "L0: Decision Core" in readme_content or "L0 (Decision Core)" in readme_content, \
            "README must document L0 Decision Core"
        
        # Check for key L0 responsibilities
        l0_section_start = readme_content.find("L0")
        l0_section = readme_content[l0_section_start:l0_section_start + 1000] if l0_section_start != -1 else readme_content
        
        assert "Evaluate" in l0_section or "evaluate" in l0_section, \
            "L0 documentation must mention state evaluation"

    def test_l1_planning_engine_documented(self, readme_content):
        """Test that L1 Planning Engine responsibilities are documented.
        
        Requirement: 12.4 - System SHALL document layer responsibilities
        """
        # Check for L1 section
        assert "L1: Planning Engine" in readme_content or "L1 (Planning Engine)" in readme_content, \
            "README must document L1 Planning Engine"
        
        # Check for key L1 characteristics
        l1_section_start = readme_content.find("L1")
        l1_section = readme_content[l1_section_start:l1_section_start + 1000] if l1_section_start != -1 else readme_content
        
        assert "Interface" in l1_section or "interface" in l1_section, \
            "L1 documentation must mention interface"

    def test_l2_execution_layer_documented(self, readme_content):
        """Test that L2 Execution Layer responsibilities are documented.
        
        Requirement: 12.4 - System SHALL document layer responsibilities
        """
        # Check for L2 section
        assert "L2: Execution Layer" in readme_content or "L2 (Execution Layer)" in readme_content, \
            "README must document L2 Execution Layer"
        
        # Check for key L2 characteristics
        l2_section_start = readme_content.find("L2")
        l2_section = readme_content[l2_section_start:l2_section_start + 1000] if l2_section_start != -1 else readme_content
        
        assert "Disabled" in l2_section or "disabled" in l2_section or "ExecutionError" in l2_section, \
            "L2 documentation must mention that execution is disabled"

    def test_authority_derivation_rules_documented(self, readme_content):
        """Test that authority derivation rules are documented.
        
        Requirement: 12.5 - System SHALL document authority derivation rules
        """
        assert "Authority Derivation Rules" in readme_content, \
            "README must have 'Authority Derivation Rules' section"
        
        # Check for state-to-authority mappings
        assert "OVERLOADED" in readme_content, \
            "Authority derivation must document OVERLOADED state"
        assert "STRESSED" in readme_content, \
            "Authority derivation must document STRESSED state"
        assert "NORMAL" in readme_content, \
            "Authority derivation must document NORMAL state"

    def test_authority_derivation_permissions_documented(self, readme_content):
        """Test that authority permissions are documented.
        
        Requirement: 12.5 - System SHALL document authority derivation rules
        """
        # Check for permission types
        assert "Planning Permission" in readme_content or "planning" in readme_content.lower(), \
            "Authority derivation must document planning permission"
        assert "Execution Permission" in readme_content or "execution" in readme_content.lower(), \
            "Authority derivation must document execution permission"
        
        # Check for permission values
        assert "ALLOWED" in readme_content or "DENIED" in readme_content, \
            "Authority derivation must document permission values (ALLOWED/DENIED)"

    def test_authority_modes_documented(self, readme_content):
        """Test that authority modes are documented.
        
        Requirement: 12.5 - System SHALL document authority derivation rules
        """
        # Check for authority modes
        assert "CONTAINMENT" in readme_content, \
            "Authority derivation must document CONTAINMENT mode"
        assert "NORMAL" in readme_content, \
            "Authority derivation must document NORMAL mode"

    def test_global_authority_enforcement_documented(self, readme_content):
        """Test that Global Authority enforcement is documented.
        
        Requirement: 12.5 - System SHALL document authority derivation rules
        """
        assert "Global Authority" in readme_content, \
            "README must document Global Authority concept"
        
        # Check for authority enforcement explanation
        authority_section = readme_content[readme_content.find("Global Authority"):] if "Global Authority" in readme_content else readme_content
        
        assert "derived" in authority_section.lower() or "Decision Core" in authority_section, \
            "README must explain that authority is derived from Decision Core"
