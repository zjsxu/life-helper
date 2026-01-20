# Requirements Document: v0.3 验证测试套件

## Introduction

v0.3 验证测试套件验证 PLO 系统的 5 个核心维度：状态判定、权限管理、拒绝能力、建议功能、安全边界。

## Glossary

- **System**: Personal Life Orchestrator (PLO) 系统
- **Decision_Core**: L0 层 - 状态评估和判定核心
- **Authority_System**: 权限管理系统
- **Containment**: 系统拒绝机制
- **Advisory_Layer**: L1 层 - 规划建议层
- **Safety_Boundary**: 安全边界
- **System_State**: 系统状态 - NORMAL, STRESSED, OVERLOADED

## Requirements

### Requirement 1: Decision Core - 状态判定正确性

**User Story:** 作为验证者，我想验证 Decision Core 是否正确判定系统状态。

#### Acceptance Criteria

1. WHEN 输入满足 OVERLOADED 阈值 THEN THE Decision_Core SHALL 判定为 OVERLOADED
2. WHEN 输入满足 STRESSED 阈值 THEN THE Decision_Core SHALL 判定为 STRESSED
3. WHEN 输入满足 NORMAL 条件 THEN THE Decision_Core SHALL 判定为 NORMAL
4. WHEN 相同输入被提供多次 THEN THE Decision_Core SHALL 产生相同判定
5. THE Decision_Core SHALL 为每个判定提供明确理由

### Requirement 2: Authority - 权限随状态变化

**User Story:** 作为验证者，我想验证权限是否正确随状态变化。

#### Acceptance Criteria

1. WHEN System_State 为 OVERLOADED THEN THE Authority_System SHALL 设置 planning_permission 为 DENIED
2. WHEN System_State 为 STRESSED THEN THE Authority_System SHALL 设置 planning_permission 为 DENIED
3. WHEN System_State 为 NORMAL THEN THE Authority_System SHALL 设置 planning_permission 为 ALLOWED
4. THE Authority_System SHALL 始终设置 execution_permission 为 DENIED
5. THE Authority_System SHALL 所有权限都派生自 Decision_Core 输出

### Requirement 3: Containment - 系统拒绝能力

**User Story:** 作为验证者，我想验证系统是否敢于拒绝用户请求。

#### Acceptance Criteria

1. WHEN planning_permission 为 DENIED THEN THE Advisory_Layer SHALL 拒绝提供建议
2. WHEN execution_permission 为 DENIED THEN THE System SHALL 拒绝执行任何自动化操作
3. WHEN 用户请求被拒绝 THEN THE System SHALL 提供明确的拒绝原因
4. THE System SHALL 在拒绝时引用 Decision_Core 的判定
5. WHEN 连续多次请求被拒绝 THEN THE System SHALL 保持一致的拒绝行为

### Requirement 4: L1 Advisory - 建议功能

**User Story:** 作为验证者，我想验证系统是否在"允许时"正确提供建议。

#### Acceptance Criteria

1. WHEN planning_permission 为 ALLOWED THEN THE Advisory_Layer SHALL 提供规划建议
2. WHEN planning_permission 为 DENIED THEN THE Advisory_Layer SHALL 不提供任何建议
3. WHEN 提供建议时 THEN THE Advisory_Layer SHALL 使用描述性语言而非指令性语言
4. THE Advisory_Layer SHALL 不修改任何输入数据
5. THE Advisory_Layer SHALL 不安排具体时间
6. THE Advisory_Layer SHALL 不执行任何自动化操作

### Requirement 5: Safety Boundary - 安全边界

**User Story:** 作为验证者，我想验证系统能够证明自己不会越权。

#### Acceptance Criteria

1. THE System SHALL 证明 execution_permission 在所有状态下都为 DENIED
2. THE System SHALL 证明 Advisory_Layer 从不调用 Execution Layer
3. THE System SHALL 证明所有权限都派生自 Decision_Core
4. THE System SHALL 证明没有任何层可以绕过 Authority_System
5. WHEN 尝试调用 Execution Layer THEN THE System SHALL 立即失败并抛出 ExecutionError

### Requirement 6: 测试输出和可验证性

**User Story:** 作为验证者，我想要清晰的测试输出格式。

#### Acceptance Criteria

1. THE System SHALL 为每个维度输出独立的测试结果
2. WHEN 测试通过 THEN THE System SHALL 输出 "PASS" 标记
3. WHEN 测试失败 THEN THE System SHALL 输出 "FAIL" 标记和详细原因
4. THE System SHALL 输出每个维度的通过率
5. THE System SHALL 输出总体验证结果摘要
