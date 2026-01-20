# v0.3-stable Frozen Component Baseline

This document records the baseline file hashes for frozen components in v0.3-stable.
These components are immutable and must not be modified by any future features.

## Git Tag

**Tag**: `v0.3-stable`
**Commit**: `f3931b9`
**Message**: v0.3-stable: Freeze Decision Core and Authority layer - immutable baseline

## Frozen Components

The following components are frozen and must remain byte-for-byte identical:

### Decision Core

- **evaluator.py**: State evaluation logic
- **rules.py**: Rule engine for downgrade rules
- **recovery.py**: Recovery monitoring

### Global Authority

- **authority.py**: Authority derivation system

### Configuration

- **config.yaml**: Thresholds and downgrade_rules sections

## Baseline File Hashes (SHA-256)

```
846946564501a609d336d5eb26322dabfc6d30e37b6bce923f29b4712b9e5f99  pl_dss/evaluator.py
bfe1b4341de95faa0e623627841ca2b37bbffc5709ed73caed7c82af662bee39  pl_dss/rules.py
20a249b21bf98435bc2e464909294ff2fb0b673ee71c9dd9030a5ff8431d876b  pl_dss/authority.py
f8e8afc019d37a299cf5ffa3e31a6a9e5ff23e36ba2a1f5377c77dfe7305002e  pl_dss/recovery.py
3d800d6261b1735d9fadf16809995acad4c8ac0753f132bdd7b2e1d97a58c4fb  config.yaml
```

## Verification

To verify that frozen components remain unchanged, run:

```bash
shasum -a 256 pl_dss/evaluator.py pl_dss/rules.py pl_dss/authority.py pl_dss/recovery.py config.yaml
```

Compare the output with the baseline hashes above. Any difference indicates a violation of the immutability guarantee.

## System Constitution

As documented in the System Constitution:

- Decision Core is the sole authority
- Authority derives exclusively from Decision Core
- Agents may analyze but never decide
- Execution is disabled by design
- No automation may bypass authority checks

**No future feature may bypass or modify these frozen layers.**

## Date

Frozen: January 20, 2026
