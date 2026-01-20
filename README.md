# Personal Life Decision-Support System (PL-DSS)

A minimal, deterministic CLI and GUI tool that evaluates your current state (normal, stressed, or overloaded) and provides pre-defined behavioral constraints to prevent collapse.

**[中文文档 (Chinese Documentation)](README_CN.md)** | **[快速启动 (Quick Start)](QUICKSTART_CN.md)**

## Features

- 🖥️ **Dual Interface**: Command-line (CLI) and Graphical (GUI) modes
- 🎯 **State Evaluation**: Assess your current state based on deadlines, workload, and energy
- 📋 **Behavioral Rules**: Get pre-defined constraints when stressed or overloaded
- 🔄 **Recovery Monitoring**: Know when it's safe to return to normal mode
- ⚙️ **Configurable**: Customize thresholds and rules via YAML config
- 🚀 **Fast & Local**: Runs locally in ~0.1 seconds, no external APIs

## Quick Start

### GUI Mode (Recommended for daily use)

**在项目根目录运行：**
```bash
python run_gui.py
```

或使用模块方式：
```bash
python -m pl_dss.gui
```

### CLI Mode (For automation/scripting)
```bash
python -m pl_dss.main --deadlines 4 --domains 3 --energy 2 3 2
```

See [GUI_GUIDE.md](GUI_GUIDE.md) for detailed GUI usage instructions.

## What This System Does

PL-DSS helps you recognize when to slow down, stop, or recover by:

- **Evaluating your current state** based on three manual inputs:
  - Number of fixed deadlines in the next 14 days
  - Number of active high-load life domains (work projects, family crises, health issues, etc.)
  - Your energy scores for the last 3 days (1-5 scale)

- **Providing behavioral constraints** when you're stressed or overloaded:
  - Pre-defined rules to prevent taking on too much
  - Clear guidance on what to pause or reduce

- **Monitoring recovery** to tell you when it's safe to return to normal mode:
  - Checks if deadlines have cleared
  - Verifies high-load domains have reduced
  - Confirms energy levels have stabilized

## What This System Does NOT Do

PL-DSS is explicitly **NOT**:

- ❌ A productivity tool or task manager
- ❌ A calendar system or deadline tracker
- ❌ An AI or machine learning system
- ❌ A database or cloud service
- ❌ A notification system
- ❌ A web scraping tool
- ❌ An authentication system

It is a simple, local, rule-based evaluation tool. You provide the inputs manually.

## How to Use Weekly

**Recommended Pattern: Weekly Check-In**

This system is designed for weekly evaluation, not daily tracking. Run it once per week to assess your state and adjust your behavior accordingly.

### Step-by-Step Weekly Workflow

1. **Every Sunday evening** (or your preferred check-in time):
   - **Count fixed deadlines**: How many non-movable deadlines do you have in the next 14 days?
   - **Count high-load domains**: How many life areas are demanding high cognitive load right now? (Examples: major work project, family crisis, health issue, moving house, etc.)
   - **Rate your energy**: On a 1-5 scale, how was your energy for the last 3 days? (1=exhausted, 5=energized)

2. **Run the system**:
   ```bash
   python -m pl_dss.main --deadlines 4 --domains 3 --energy 2 3 2
   ```
   Or run interactively:
   ```bash
   python -m pl_dss.main
   ```

3. **Review the output**:
   - See your current state (NORMAL, STRESSED, or OVERLOADED)
   - Read the explanation of why you're in that state
   - Note any behavioral constraints if stressed or overloaded
   - Check recovery status to know when you can ease up

4. **Adjust your week accordingly**:
   - **If OVERLOADED**: Follow all downgrade rules strictly. Say no to new commitments.
   - **If STRESSED**: Be cautious about new projects. Create time buffers.
   - **If NORMAL**: Proceed with normal activities. You have capacity.

5. **Repeat next week**: Check in again next Sunday to reassess your state.

## Personal Life Orchestrator (PLO)

The Personal Life Orchestrator extends PL-DSS with a **safety-first layered architecture** that enforces strict control boundaries. PLO demonstrates how the Decision Core can safely govern higher-level automation through explicit authority derivation.

### What PLO Does

PLO adds three architectural layers on top of the Decision Core:

- **L0 (Decision Core)**: The existing PL-DSS that evaluates your state
- **L1 (Planning Engine)**: Interface for future planning functionality (not yet implemented)
- **L2 (Execution Layer)**: Explicitly disabled automation layer

**Key Feature: Global Authority Enforcement**

All downstream operations are controlled by a **Global Authority** object derived from the Decision Core's state evaluation:

- **When OVERLOADED or STRESSED**: Planning is DENIED, mode is CONTAINMENT
- **When NORMAL**: Planning is ALLOWED, mode is NORMAL
- **Always**: Execution is DENIED (automation is disabled in this version)

This ensures that **automation can NEVER override safety decisions** from the Decision Core.

### What PLO Refuses to Do

PLO is designed with explicit safety boundaries:

- ❌ **No autonomous execution**: The Execution Layer always raises an error if called
- ❌ **No planning when unsafe**: Planning is blocked when you're stressed or overloaded
- ❌ **No "smart" behavior**: The system is boring and conservative by design
- ❌ **No override mechanisms**: There is no way to bypass authority checks

**The system fails loudly when safety boundaries are violated.**

### How PLO Will Expand Safely

PLO is designed for incremental, safety-first expansion:

**Current Phase (Phase 1): Authority Foundation**
- Global Authority derivation from Decision Core
- Planning Engine interface (not implemented)
- Execution Layer explicitly disabled
- Scenario-based demonstration of authority enforcement

**Future Phase 2: Planning Implementation**
- Implement scheduling algorithms in Planning Engine
- Add task and constraint data structures
- Implement conflict detection
- Still respect Global Authority (no planning when denied)

**Future Phase 3: Controlled Execution**
- Enable execution only when explicitly safe
- Implement execution hooks with safety checks
- Add execution audit logging
- Maintain authority enforcement

**Future Phase 4: Full Autonomy**
- Autonomous planning and execution
- Self-monitoring and adjustment
- Advanced recovery strategies
- Always respect Decision Core authority

**Safety Principle**: Each phase builds on the previous one, and the Decision Core always has final authority over all operations.

### PLO Layer Responsibilities

#### L0: Decision Core (Existing PL-DSS)
- **Purpose**: Evaluate system state and determine safety
- **Inputs**: Deadlines, workload domains, energy scores
- **Outputs**: State (NORMAL/STRESSED/OVERLOADED), downgrade rules
- **Independence**: Operates without knowledge of L1 or L2
- **Modification**: Never modified by PLO (preserved as-is)

#### L1: Planning Engine (Interface Only)
- **Purpose**: Future planning functionality interface
- **Current State**: Interface defined, not implemented
- **Authority Check**: Always checks Global Authority before proceeding
- **Behavior When Denied**: Returns None + "Planning blocked by Decision Core"
- **Behavior When Allowed**: Returns None + "Planning interface not yet implemented"
- **Future**: Will implement scheduling, conflict detection, feasibility analysis

#### L2: Execution Layer (Explicitly Disabled)
- **Purpose**: Placeholder for future automation
- **Current State**: Always raises ExecutionError
- **Error Message**: "Automation disabled in current system version"
- **Authority Check**: Checks Global Authority (always denied)
- **Future**: Will implement safe automation hooks with audit logging

### Authority Derivation Rules

The Global Authority object is derived from Decision Core output using these rules:

| Decision Core State | Planning Permission | Execution Permission | Authority Mode |
|---------------------|---------------------|----------------------|----------------|
| OVERLOADED          | DENIED              | DENIED               | CONTAINMENT    |
| STRESSED            | DENIED              | DENIED               | CONTAINMENT    |
| NORMAL              | ALLOWED             | DENIED*              | NORMAL         |

*Execution is always DENIED in the current system version (Phase 1).

**Authority Flow:**
```
Decision Core → Global Authority → Planning Engine
                                 → Execution Layer
```

All downstream layers must check Global Authority before any operation. There is no way to bypass this check.

### Using PLO

PLO provides a CLI for running scenarios that demonstrate authority enforcement:

**Run a single scenario:**
```bash
python -m pl_dss.plo_cli scenario run --name "Sudden Load Spike"
```

**Run all scenarios:**
```bash
python -m pl_dss.plo_cli scenario run-all
```

**Evaluate current state with authority:**
```bash
python -m pl_dss.plo_cli evaluate --deadlines 4 --domains 3 --energy 2 3 2
```

**Validate scenario file:**
```bash
python -m pl_dss.plo_cli scenario validate --file scenarios/test_scenarios.yaml
```

**Example Output:**
```
SCENARIO: Sudden Load Spike
STATE: OVERLOADED
AUTHORITY:
- planning: DENIED
- execution: DENIED
MODE: CONTAINMENT
ACTIVE RULES:
- No new commitments
- Pause non-essential work
```

### PLO Configuration

PLO extends `config.yaml` with authority derivation rules:

```yaml
# Existing Decision Core configuration
thresholds:
  overload:
    fixed_deadlines_14d: 3
    active_high_load_domains: 3
    avg_energy_score: 2
  recovery:
    fixed_deadlines_14d: 1
    active_high_load_domains: 2
    avg_energy_score: 4

# PLO authority derivation
authority_derivation:
  OVERLOADED:
    planning: DENIED
    execution: DENIED
    mode: CONTAINMENT
  STRESSED:
    planning: DENIED
    execution: DENIED
    mode: CONTAINMENT
  NORMAL:
    planning: ALLOWED
    execution: DENIED
    mode: NORMAL
```

### PLO Design Philosophy

- **Safety-First**: Fail loudly when boundaries are violated
- **Boring and Conservative**: No "smart" behavior without explicit permission
- **Layered Architecture**: Clear separation of concerns (L0, L1, L2)
- **Authority Enforcement**: Decision Core has final say over all operations
- **Incremental Expansion**: Each phase builds safely on the previous one
- **Explicit Denial**: Prefer explicit denial over implicit permission
- **Demonstrable Correctness**: Scenario-based validation without GUI

## Installation

1. **Ensure Python 3.8+ is installed**
   ```bash
   python --version  # Should be 3.8 or higher
   ```

2. **Install dependencies**:
   ```bash
   pip install pyyaml
   ```

3. **(Optional) Install testing dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   ```

## Usage

### GUI Mode (Graphical Interface)

Launch the graphical interface:
```bash
python run_gui.py
```

The GUI provides:
- **Input fields** for deadlines, domains, and energy scores
- **Evaluate button** to assess your state
- **Results display** with color-coded state and detailed explanations
- **User-friendly interface** in Chinese

### CLI Mode (Command Line)

For command-line usage:

**Run with command-line arguments:**
```bash
python -m pl_dss.main --deadlines 4 --domains 3 --energy 2 3 2
```

**Run interactively:**
```bash
python -m pl_dss.main
```

## Configuration

Edit `config.yaml` to customize:
- Thresholds for state evaluation
- Downgrade rules for each state
- Recovery conditions

## Running Tests

```bash
pytest tests/
```

## Design Philosophy

- **Minimal**: Core logic under 100 lines
- **Deterministic**: Same inputs always produce same outputs
- **Local**: No external API calls or cloud dependencies
- **Transparent**: All rules are visible and configurable
- **Simple**: Standard library preferred, minimal dependencies

