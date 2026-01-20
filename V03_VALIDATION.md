# v0.3 验证测试套件

## 概述

v0.3 验证测试套件验证 PLO 系统的 5 个核心维度：

1. **Decision Core** - 状态判定正确性
2. **Authority** - 权限随状态变化
3. **Containment** - 系统拒绝能力
4. **L1 Advisory** - 建议功能
5. **Safety Boundary** - 安全边界

## 运行测试

### 运行所有测试

```bash
python -m pl_dss.plo_cli validate-v03
```

### 运行特定维度的测试

```bash
# Decision Core 测试
python -m pl_dss.plo_cli validate-v03 --dimension decision-core

# Authority 测试
python -m pl_dss.plo_cli validate-v03 --dimension authority

# Containment 测试
python -m pl_dss.plo_cli validate-v03 --dimension containment

# Advisory 测试
python -m pl_dss.plo_cli validate-v03 --dimension advisory

# Safety Boundary 测试
python -m pl_dss.plo_cli validate-v03 --dimension safety-boundary
```

### 详细输出模式

```bash
python -m pl_dss.plo_cli validate-v03 --verbose
```

## 直接使用 pytest

你也可以直接使用 pytest 运行测试：

```bash
# 运行所有测试
pytest tests/test_v03_validation.py -v

# 运行特定测试类
pytest tests/test_v03_validation.py::TestDecisionCore -v
pytest tests/test_v03_validation.py::TestAuthority -v
pytest tests/test_v03_validation.py::TestContainment -v
pytest tests/test_v03_validation.py::TestAdvisory -v
pytest tests/test_v03_validation.py::TestSafetyBoundary -v
```

## 测试覆盖

### Dimension 1: Decision Core
- ✓ OVERLOADED 状态判定
- ✓ STRESSED 状态判定
- ✓ NORMAL 状态判定
- ✓ 判定理由完整性

### Dimension 2: Authority
- ✓ OVERLOADED 状态拒绝规划
- ✓ STRESSED 状态拒绝规划
- ✓ NORMAL 状态允许规划
- ✓ 执行权限始终为 DENIED
- ✓ 权限派生自 Decision Core

### Dimension 3: Containment
- ✓ 规划被拒绝时的行为
- ✓ 执行始终被拒绝
- ✓ 拒绝消息清晰明确
- ✓ 拒绝消息引用 Decision Core

### Dimension 4: L1 Advisory
- ✓ ALLOWED 时提供建议
- ✓ DENIED 时不提供建议
- ✓ 使用描述性语言
- ✓ 不修改输入数据

### Dimension 5: Safety Boundary
- ✓ 执行权限在所有状态下都为 DENIED
- ✓ Advisory Layer 不调用 Execution Layer
- ✓ 所有权限派生自 Decision Core
- ✓ 无法绕过 Authority System
- ✓ 调用 Execution Layer 立即失败

## 预期输出

成功运行时，你会看到：

```
======================================================================
v0.3 VALIDATION: ALL TESTS PASSED
======================================================================

5 Core Dimensions Validated:
  ✓ Dimension 1: Decision Core - 状态判定正确性
  ✓ Dimension 2: Authority - 权限随状态变化
  ✓ Dimension 3: Containment - 系统拒绝能力
  ✓ Dimension 4: L1 Advisory - 建议功能
  ✓ Dimension 5: Safety Boundary - 安全边界
```

## 退出码

- `0`: 所有测试通过
- `非零`: 至少有一个测试失败

## CI/CD 集成

在 CI/CD 流程中使用：

```bash
# 在 CI 脚本中
python -m pl_dss.plo_cli validate-v03
if [ $? -ne 0 ]; then
    echo "v0.3 validation failed"
    exit 1
fi
```
