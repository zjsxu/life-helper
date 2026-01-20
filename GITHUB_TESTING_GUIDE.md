# GitHub Interface Testing Guide

This guide explains how to test the GitHub Interface Integration for the Personal Life Orchestrator.

## Table of Contents

1. [Testing the Glue Script Standalone](#testing-the-glue-script-standalone)
2. [Testing with Sample Issues](#testing-with-sample-issues)
3. [Verifying Immutability](#verifying-immutability)
4. [Running Automated Tests](#running-automated-tests)
5. [Testing with Real GitHub Issues](#testing-with-real-github-issues)

---

## Testing the Glue Script Standalone

The glue script (`scripts/run_from_issue.py`) can be tested independently without GitHub Actions.

### Basic Usage

```bash
# Test with a valid Issue body
python scripts/run_from_issue.py "### Non-movable deadlines (next 14 days)

1

### Active high-load domains

1

### Energy (1–5, comma-separated)

4,4,5

### Tasks / commitments

Review PR #123"
```

### Using Sample Issues

The repository includes pre-defined sample Issue bodies in `tests/sample_issues.py`:

```bash
# Test with NORMAL state sample
python -c "from tests.sample_issues import VALID_ISSUE_NORMAL; import sys; sys.argv = ['', VALID_ISSUE_NORMAL]; exec(open('scripts/run_from_issue.py').read())"

# Or use a helper script
python -c "
from tests.sample_issues import SAMPLE_ISSUES
import subprocess
import sys

issue_body = SAMPLE_ISSUES['valid_normal']
result = subprocess.run(
    ['python', 'scripts/run_from_issue.py', issue_body],
    capture_output=True,
    text=True
)
print(result.stdout)
if result.stderr:
    print('STDERR:', result.stderr, file=sys.stderr)
"
```

### Expected Output Format

Valid inputs should produce output in this format:

```
=== Personal Decision-Support System ===

Current State: NORMAL
Reason: All metrics within normal range

Planning: ALLOWED
Execution: DENIED

Authority Mode: NORMAL

Recovery Status: Ready
```

### Testing Error Cases

```bash
# Test missing field
python scripts/run_from_issue.py "### Non-movable deadlines (next 14 days)

1

### Energy (1–5, comma-separated)

3,3,3"

# Expected: ERROR: Missing required field: domains

# Test invalid energy format
python scripts/run_from_issue.py "### Non-movable deadlines (next 14 days)

1

### Active high-load domains

1

### Energy (1–5, comma-separated)

3,3"

# Expected: ERROR: Energy must be exactly 3 comma-separated integers
```

---

## Testing with Sample Issues

The `tests/sample_issues.py` file contains comprehensive test data covering:

### Valid Scenarios

- **NORMAL state**: Low stress, good energy
- **STRESSED state**: Moderate stress
- **OVERLOADED state**: High stress, low energy
- **No tasks**: Minimal valid input

### Invalid Scenarios

- Missing required fields (deadlines, domains, energy)
- Bad energy format (wrong count, out of range)
- Non-integer values for numeric fields

### Edge Cases

- Boundary values (exact thresholds)
- Maximum/minimum valid values
- Extra whitespace
- Empty optional fields

### Using Sample Issues in Tests

```python
from tests.sample_issues import SAMPLE_ISSUES

# Access specific samples
normal_issue = SAMPLE_ISSUES["valid_normal"]
overloaded_issue = SAMPLE_ISSUES["valid_overloaded"]
invalid_issue = SAMPLE_ISSUES["invalid_missing_deadlines"]

# Test parsing
from scripts.run_from_issue import parse_issue_body

try:
    inputs = parse_issue_body(normal_issue)
    print(f"Parsed successfully: {inputs}")
except ValueError as e:
    print(f"Parsing failed: {e}")
```

### Manual Testing Script

Create a test script to iterate through all samples:

```python
#!/usr/bin/env python3
"""Test all sample Issues."""

import sys
from tests.sample_issues import SAMPLE_ISSUES
from scripts.run_from_issue import parse_issue_body, main

def test_all_samples():
    """Test parsing all sample Issues."""
    print("Testing all sample Issues...\n")
    
    for name, issue_body in SAMPLE_ISSUES.items():
        print(f"Testing: {name}")
        print("-" * 60)
        
        try:
            inputs = parse_issue_body(issue_body)
            print(f"✓ Parsed successfully")
            print(f"  Deadlines: {inputs.fixed_deadlines_14d}")
            print(f"  Domains: {inputs.active_high_load_domains}")
            print(f"  Energy: {inputs.energy_scores_last_3_days}")
        except ValueError as e:
            print(f"✗ Parsing failed: {e}")
        
        print()

if __name__ == "__main__":
    test_all_samples()
```

Save as `test_samples.py` and run:

```bash
python test_samples.py
```

---

## Verifying Immutability

The GitHub Interface must NOT modify frozen components. Here's how to verify:

### 1. Check Git Status

```bash
# Ensure no modifications to frozen files
git status

# Should show NO changes to:
# - pl_dss/evaluator.py
# - pl_dss/rules.py
# - pl_dss/authority.py
# - pl_dss/recovery.py
# - config.yaml (thresholds section)
```

### 2. Compare with v0.3-stable Tag

```bash
# Compare frozen files with tagged version
git diff v0.3-stable -- pl_dss/evaluator.py
git diff v0.3-stable -- pl_dss/rules.py
git diff v0.3-stable -- pl_dss/authority.py
git diff v0.3-stable -- pl_dss/recovery.py

# Should show NO differences
```

### 3. Run Immutability Tests

```bash
# Run automated immutability verification
pytest tests/test_immutability.py -v

# This test compares file hashes with baseline
```

### 4. Verify File Hashes

```bash
# Generate current hashes
sha256sum pl_dss/evaluator.py
sha256sum pl_dss/rules.py
sha256sum pl_dss/authority.py
sha256sum pl_dss/recovery.py

# Compare with documented baseline hashes in V03_FROZEN_BASELINE.md
```

### 5. Check Code Reuse

```bash
# Verify glue script imports existing functions
grep "from pl_dss" scripts/run_from_issue.py

# Should show imports like:
# from pl_dss.config import load_config
# from pl_dss.evaluator import StateInputs, evaluate_state
# from pl_dss.authority import derive_authority
# from pl_dss.recovery import check_recovery
```

### Immutability Checklist

- [ ] No modifications to `pl_dss/evaluator.py`
- [ ] No modifications to `pl_dss/rules.py`
- [ ] No modifications to `pl_dss/authority.py`
- [ ] No modifications to `pl_dss/recovery.py`
- [ ] No modifications to `config.yaml` thresholds
- [ ] Glue script imports existing functions (no duplication)
- [ ] All tests pass
- [ ] File hashes match v0.3-stable baseline

---

## Running Automated Tests

### Run All Tests

```bash
# Run complete test suite
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=pl_dss --cov=scripts --cov-report=html
```

### Run Specific Test Categories

```bash
# GitHub integration tests (parsing, glue script)
pytest tests/test_github_integration.py -v

# Authority enforcement tests
pytest tests/test_authority_enforcement.py -v

# Immutability tests
pytest tests/test_immutability.py -v

# Code reuse tests
pytest tests/test_code_reuse.py -v

# Integration tests (end-to-end)
pytest tests/test_integration.py -v
```

### Run Property-Based Tests

```bash
# Run with Hypothesis (property-based testing)
pytest tests/ -v --hypothesis-show-statistics

# Run with more iterations for thorough testing
pytest tests/ -v --hypothesis-seed=random
```

### Test Output Consistency

```bash
# Verify CLI and GitHub produce identical output
pytest tests/test_integration.py::test_cli_github_consistency -v
```

---

## Testing with Real GitHub Issues

### Prerequisites

1. Repository must be on GitHub
2. GitHub Actions must be enabled
3. Workflow file must be in `.github/workflows/life_orchestrator.yml`
4. Issue template must be in `.github/ISSUE_TEMPLATE/life_checkin.yaml`

### Step-by-Step Testing

#### 1. Create a Test Issue

1. Go to your repository on GitHub
2. Click **Issues** → **New Issue**
3. Select **"Life Check-in"** template
4. Fill in the form:
   - **Non-movable deadlines**: `1`
   - **Active high-load domains**: `1`
   - **Energy**: `4,4,5`
   - **Tasks**: `Test the GitHub interface`
5. Click **Submit new issue**

#### 2. Verify Workflow Triggers

1. Go to **Actions** tab
2. Look for workflow run named "Life Orchestrator"
3. Click on the run to see details
4. Verify:
   - Workflow triggered on Issue creation
   - Python environment set up correctly
   - Dependencies installed
   - Script executed successfully

#### 3. Check Issue Comment

1. Return to the Issue you created
2. Look for a comment from `github-actions[bot]`
3. Verify the comment contains:
   - Current State (NORMAL, STRESSED, or OVERLOADED)
   - Planning permission (ALLOWED or DENIED)
   - Execution permission (always DENIED)
   - Authority mode
   - Active rules (if applicable)
   - Recovery status

#### 4. Test Different Scenarios

Create additional Issues to test:

**OVERLOADED State**:
- Deadlines: `4`
- Domains: `3`
- Energy: `2,2,2`

**STRESSED State**:
- Deadlines: `3`
- Domains: `2`
- Energy: `3,3,2`

**Edge Cases**:
- Minimum values: `0`, `0`, `1,1,1`
- Maximum values: `10`, `10`, `5,5,5`

#### 5. Test Error Handling

Edit an Issue to introduce errors:

1. Edit the Issue
2. Remove a required field (e.g., delete the domains value)
3. Save changes
4. Verify workflow posts error comment with clear message

### Troubleshooting

**Workflow doesn't trigger**:
- Check Issue has "life-checkin" label
- Verify workflow file is in correct location
- Check GitHub Actions is enabled for repository

**Comment not posted**:
- Check workflow logs for errors
- Verify workflow has `issues: write` permission
- Check for Python errors in script execution step

**Wrong output format**:
- Verify glue script uses `format_output()` from `main.py`
- Check for modifications to frozen components
- Run immutability tests

---

## Continuous Integration

### Pre-commit Checks

Add to `.github/workflows/ci.yml`:

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      - name: Install dependencies
        run: pip install -r requirements-dev.txt
      - name: Run tests
        run: pytest tests/ -v
      - name: Verify immutability
        run: pytest tests/test_immutability.py -v
```

### Local Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Verify immutability before committing

echo "Checking frozen components..."

# Check for modifications to frozen files
FROZEN_FILES=(
    "pl_dss/evaluator.py"
    "pl_dss/rules.py"
    "pl_dss/authority.py"
    "pl_dss/recovery.py"
)

for file in "${FROZEN_FILES[@]}"; do
    if git diff --cached --name-only | grep -q "^$file$"; then
        echo "ERROR: Attempt to modify frozen file: $file"
        echo "Frozen components cannot be modified per system constitution."
        exit 1
    fi
done

echo "✓ No frozen components modified"

# Run quick tests
pytest tests/test_immutability.py -q
if [ $? -ne 0 ]; then
    echo "ERROR: Immutability tests failed"
    exit 1
fi

echo "✓ All checks passed"
exit 0
```

Make executable:

```bash
chmod +x .git/hooks/pre-commit
```

---

## Summary

### Quick Test Commands

```bash
# Test glue script with sample
python scripts/run_from_issue.py "$(python -c 'from tests.sample_issues import VALID_ISSUE_NORMAL; print(VALID_ISSUE_NORMAL)')"

# Run all automated tests
pytest tests/ -v

# Verify immutability
pytest tests/test_immutability.py -v

# Check code reuse
pytest tests/test_code_reuse.py -v

# Test end-to-end integration
pytest tests/test_integration.py -v
```

### Testing Checklist

Before deployment:

- [ ] All sample Issues parse correctly
- [ ] Error cases produce clear messages
- [ ] Glue script output matches CLI format
- [ ] All automated tests pass
- [ ] Immutability verified (no frozen file changes)
- [ ] Code reuse verified (imports existing functions)
- [ ] Integration tests pass
- [ ] Manual GitHub Issue test successful
- [ ] Workflow triggers correctly
- [ ] Comments posted with correct format

---

## Additional Resources

- **Sample Issues**: `tests/sample_issues.py`
- **Glue Script**: `scripts/run_from_issue.py`
- **Workflow**: `.github/workflows/life_orchestrator.yml`
- **Issue Template**: `.github/ISSUE_TEMPLATE/life_checkin.yaml`
- **Baseline Hashes**: `V03_FROZEN_BASELINE.md`
- **Requirements**: `.kiro/specs/github-interface/requirements.md`
- **Design**: `.kiro/specs/github-interface/design.md`
