#!/usr/bin/env python3
"""Demo script to test all sample Issues.

This demonstrates the testing procedures documented in GITHUB_TESTING_GUIDE.md
"""

import sys
from tests.sample_issues import SAMPLE_ISSUES
from scripts.run_from_issue import parse_issue_body, IssueParsingError


def test_all_samples():
    """Test parsing all sample Issues."""
    print("=" * 70)
    print("Testing All Sample Issues")
    print("=" * 70)
    print()
    
    valid_count = 0
    invalid_count = 0
    
    for name, issue_body in SAMPLE_ISSUES.items():
        print(f"Testing: {name}")
        print("-" * 70)
        
        try:
            inputs, tasks = parse_issue_body(issue_body)
            print(f"✓ Parsed successfully")
            print(f"  Deadlines: {inputs.fixed_deadlines_14d}")
            print(f"  Domains: {inputs.active_high_load_domains}")
            print(f"  Energy: {inputs.energy_scores_last_3_days}")
            if tasks:
                print(f"  Tasks: {tasks[:50]}...")
            valid_count += 1
        except IssueParsingError as e:
            print(f"✗ Parsing failed (expected for invalid samples)")
            error_lines = str(e).split('\n')
            print(f"  Error: {error_lines[0]}")
            invalid_count += 1
        except Exception as e:
            print(f"✗ Unexpected error: {type(e).__name__}: {e}")
        
        print()
    
    print("=" * 70)
    print(f"Summary: {valid_count} valid, {invalid_count} invalid")
    print("=" * 70)


if __name__ == "__main__":
    test_all_samples()
