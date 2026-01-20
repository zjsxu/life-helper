"""
Sample GitHub Issue bodies for testing the GitHub Interface Integration.

These samples cover various scenarios for testing the Issue parser and glue script.
"""

# Valid Issue - NORMAL state
# This should result in NORMAL state (low stress, good energy)
VALID_ISSUE_NORMAL = """### Non-movable deadlines (next 14 days)

1

### Active high-load domains

1

### Energy (1–5, comma-separated)

4,4,5

### Tasks / commitments

Review PR #123
Prepare presentation slides
"""

# Valid Issue - OVERLOADED state
# This should result in OVERLOADED state (high deadlines, high domains, low energy)
VALID_ISSUE_OVERLOADED = """### Non-movable deadlines (next 14 days)

4

### Active high-load domains

3

### Energy (1–5, comma-separated)

2,2,2

### Tasks / commitments

ML Homework 3 due Feb 12
Org meeting prep
Project deadline Friday
Research paper review
"""

# Valid Issue - STRESSED state
# This should result in STRESSED state (moderate stress)
VALID_ISSUE_STRESSED = """### Non-movable deadlines (next 14 days)

3

### Active high-load domains

2

### Energy (1–5, comma-separated)

3,3,2

### Tasks / commitments

Team meeting tomorrow
Code review needed
"""

# Valid Issue - No tasks (minimal valid input)
VALID_ISSUE_NO_TASKS = """### Non-movable deadlines (next 14 days)

0

### Active high-load domains

0

### Energy (1–5, comma-separated)

5,5,5

### Tasks / commitments

_No response_
"""

# Invalid Issue - Missing deadlines field
INVALID_ISSUE_MISSING_DEADLINES = """### Active high-load domains

2

### Energy (1–5, comma-separated)

3,3,3

### Tasks / commitments

Some tasks here
"""

# Invalid Issue - Missing domains field
INVALID_ISSUE_MISSING_DOMAINS = """### Non-movable deadlines (next 14 days)

2

### Energy (1–5, comma-separated)

3,3,3

### Tasks / commitments

Some tasks here
"""

# Invalid Issue - Missing energy field
INVALID_ISSUE_MISSING_ENERGY = """### Non-movable deadlines (next 14 days)

2

### Active high-load domains

1

### Tasks / commitments

Some tasks here
"""

# Invalid Issue - Bad energy format (only 2 values)
INVALID_ISSUE_BAD_ENERGY_COUNT = """### Non-movable deadlines (next 14 days)

1

### Active high-load domains

1

### Energy (1–5, comma-separated)

3,3

### Tasks / commitments

Some tasks
"""

# Invalid Issue - Bad energy format (4 values)
INVALID_ISSUE_BAD_ENERGY_TOO_MANY = """### Non-movable deadlines (next 14 days)

1

### Active high-load domains

1

### Energy (1–5, comma-separated)

3,3,3,3

### Tasks / commitments

Some tasks
"""

# Invalid Issue - Energy out of range (too high)
INVALID_ISSUE_ENERGY_OUT_OF_RANGE_HIGH = """### Non-movable deadlines (next 14 days)

1

### Active high-load domains

1

### Energy (1–5, comma-separated)

3,6,3

### Tasks / commitments

Some tasks
"""

# Invalid Issue - Energy out of range (too low)
INVALID_ISSUE_ENERGY_OUT_OF_RANGE_LOW = """### Non-movable deadlines (next 14 days)

1

### Active high-load domains

1

### Energy (1–5, comma-separated)

0,3,3

### Tasks / commitments

Some tasks
"""

# Invalid Issue - Non-integer deadlines
INVALID_ISSUE_NON_INTEGER_DEADLINES = """### Non-movable deadlines (next 14 days)

abc

### Active high-load domains

1

### Energy (1–5, comma-separated)

3,3,3

### Tasks / commitments

Some tasks
"""

# Invalid Issue - Non-integer domains
INVALID_ISSUE_NON_INTEGER_DOMAINS = """### Non-movable deadlines (next 14 days)

1

### Active high-load domains

xyz

### Energy (1–5, comma-separated)

3,3,3

### Tasks / commitments

Some tasks
"""

# Invalid Issue - Non-integer energy values
INVALID_ISSUE_NON_INTEGER_ENERGY = """### Non-movable deadlines (next 14 days)

1

### Active high-load domains

1

### Energy (1–5, comma-separated)

a,b,c

### Tasks / commitments

Some tasks
"""

# Edge case - Boundary values (exact thresholds)
EDGE_CASE_BOUNDARY_VALUES = """### Non-movable deadlines (next 14 days)

2

### Active high-load domains

2

### Energy (1–5, comma-separated)

3,3,3

### Tasks / commitments

Testing boundary conditions
"""

# Edge case - Maximum valid values
EDGE_CASE_MAX_VALUES = """### Non-movable deadlines (next 14 days)

10

### Active high-load domains

10

### Energy (1–5, comma-separated)

5,5,5

### Tasks / commitments

Maximum stress test
"""

# Edge case - Minimum valid values
EDGE_CASE_MIN_VALUES = """### Non-movable deadlines (next 14 days)

0

### Active high-load domains

0

### Energy (1–5, comma-separated)

1,1,1

### Tasks / commitments

Minimum stress test
"""

# Edge case - Whitespace variations
EDGE_CASE_EXTRA_WHITESPACE = """### Non-movable deadlines (next 14 days)

  2  

### Active high-load domains

  1  

### Energy (1–5, comma-separated)

  3 , 3 , 3  

### Tasks / commitments

Testing whitespace handling
"""

# Edge case - Empty tasks field
EDGE_CASE_EMPTY_TASKS = """### Non-movable deadlines (next 14 days)

1

### Active high-load domains

1

### Energy (1–5, comma-separated)

3,3,3

### Tasks / commitments


"""

# Dictionary for easy access
SAMPLE_ISSUES = {
    "valid_normal": VALID_ISSUE_NORMAL,
    "valid_overloaded": VALID_ISSUE_OVERLOADED,
    "valid_stressed": VALID_ISSUE_STRESSED,
    "valid_no_tasks": VALID_ISSUE_NO_TASKS,
    "invalid_missing_deadlines": INVALID_ISSUE_MISSING_DEADLINES,
    "invalid_missing_domains": INVALID_ISSUE_MISSING_DOMAINS,
    "invalid_missing_energy": INVALID_ISSUE_MISSING_ENERGY,
    "invalid_bad_energy_count": INVALID_ISSUE_BAD_ENERGY_COUNT,
    "invalid_bad_energy_too_many": INVALID_ISSUE_BAD_ENERGY_TOO_MANY,
    "invalid_energy_out_of_range_high": INVALID_ISSUE_ENERGY_OUT_OF_RANGE_HIGH,
    "invalid_energy_out_of_range_low": INVALID_ISSUE_ENERGY_OUT_OF_RANGE_LOW,
    "invalid_non_integer_deadlines": INVALID_ISSUE_NON_INTEGER_DEADLINES,
    "invalid_non_integer_domains": INVALID_ISSUE_NON_INTEGER_DOMAINS,
    "invalid_non_integer_energy": INVALID_ISSUE_NON_INTEGER_ENERGY,
    "edge_boundary_values": EDGE_CASE_BOUNDARY_VALUES,
    "edge_max_values": EDGE_CASE_MAX_VALUES,
    "edge_min_values": EDGE_CASE_MIN_VALUES,
    "edge_extra_whitespace": EDGE_CASE_EXTRA_WHITESPACE,
    "edge_empty_tasks": EDGE_CASE_EMPTY_TASKS,
}
